import flask 
from flask import request, jsonify
from flask_restful import  Api, Resource
from resources.users import Users, User
from resources.accounts import Accounts , Account    #account
import pymysql


app = flask.Flask(__name__)
app.config['DEGUG'] = True

api = Api(app)
api.add_resource(Users, '/users')    #這個users是自己定義的，網址上的分頁
api.add_resource(User, '/users/<id>')       #flask自己定義的表達方式 <id> 將users.py 裡的id數字帶入
api.add_resource(Accounts, '/account')    
api.add_resource(Account, '/account/<id>')
#----------------錯誤不會揭露給使用者看--------------------
@app.errorhandler(Exception)     #Exception 來自python裡
def hendle(error):                #error 來自 Exception
    status_code = 500
    if type(error).__name__ == 'NotFound':
        code = 404
    return{
        'msg':type(error).__name__
    },code

#------------------------驗證授權----------------------
@app.before_request
def auth():
    token = request.headers.get('auth')    #auth是自己定義的，在postman的key裡設定auth
    if token == '567':                  #如果auth打勾就會pass，在users裡有設定201
        pass                            #否則status會跳401
    else:
        return {
            'msg':'invalid token',
       },401


#-----------------------------重構----------------------------
def get_account(account_number):
    db = pymysql.connect(            #連接資料庫
    '192.168.56.103',            #資料庫所在ip
    'Neil',                      #user
    'Pn123456',                   #密碼
    'flask_schema'                
    )
    cursor = db.cursor(pymysql.cursors.DictCursor)
    sql = """
        select * from flask_schema.accounts Where account_number = {};
    """.format(account_number)
    cursor.execute(sql)
    return db, cursor, account_number


#----------------------------存錢------------------------------------
@app.route('/account/<account_number>/deposit', methods = ['post'])
def deposit(account_number):
    db = pymysql.connect(            #連接資料庫
    '192.168.56.103',            #資料庫所在ip
    'Neil',                      #user
    'Pn123456',                   #密碼
    'flask_schema'                #db名
    )
    cursor = db.cursor(pymysql.cursors.DictCursor)
    sql = """
        select * from flask_schema.accounts Where account_number = {};
    """.format(account_number)
    cursor.execute(sql)
    account = cursor.fetchone()
    money = request.values['money']      #['money']在postman 裡指定來的（由前端）
    balance = account['balance'] + int(money)

    sql = """UPDATE `flask_schema`.`accounts` 
        SET `balance` = {}
        WHERE account_number = {};
        """.format(balance, account_number)
    result = cursor.execute(sql)
    db.commit()
    db.close()
    response = {'code':200, 'msg':'success'}
    if result == 0:
        response['msg'] = 'error'
    return jsonify(response)

#-----------------------------領錢-------------------------------------
@app.route('/account/<account_number>/withdraw', methods = ['post'])
def withdraw(account_number):
    # db = pymysql.connect(            #連接資料庫
    # '192.168.56.103',            #資料庫所在ip
    # 'Neil',                      #user
    # 'Pn123456',                   #密碼
    # 'flask_schema'                #db名
    # )
    # cursor = db.cursor(pymysql.cursors.DictCursor)
    # sql = """
    #     select * from flask_schema.accounts Where account_number = {};
    # """.format(account_number)
    # cursor.execute(sql)
    db, cursor, account_number = get_account(account_number)
    
    account = cursor.fetchone()
    money = request.values['money']      #['money']在postman 裡指定來的（由前端）
    balance = account['balance'] - int(money)
    response = {'code':200, 'msg':'success'}

    if balance < 0:                   #在update前
        response['msg'] = 'error'
        response['code'] = 400
        return jsonify(response)
    else:
        sql = """UPDATE `flask_schema`.`accounts` 
            SET `balance` = {}
            WHERE account_number = {};
            """.format(balance, account_number)
        result = cursor.execute(sql)
        db.commit()
        db.close()
        response = {'code':200, 'msg':'success'}
        if result == 0:
            response['msg'] = 'error'
        return jsonify(response)



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=35)   #flask 的位置，網頁上要打localhost:34
