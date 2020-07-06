from flask import jsonify      
from flask_restful import  Api, Resource, reqparse
import pymysql

parser = reqparse.RequestParser()   #post
parser.add_argument('balance')
parser.add_argument('account_number')
parser.add_argument('user_id')
parser.add_argument('deleted')


class Accounts(Resource):
#--------------------------登入資料庫----------------------------------
    def db_init(self):
        db = pymysql.connect(            #連接資料庫
            '192.168.56.103',            #資料庫所在ip
            'Neil',                      #user
            'Pn123456',                   #密碼
            'flask_schema'                #db名
        )
        cursor = db.cursor(pymysql.cursors.DictCursor)
        return db, cursor
#---------------------------get--------------------------------------
    def get(self):
        db, cursor = self.db_init()
        sql = 'select * from flask_schema.accounts Where deleted = False;'
        cursor.execute(sql)
        accounts = cursor.fetchall()          #fetchall() 抓全部
        db.close()
        return jsonify(accounts)          # 以json格式顯示，需要import
#---------------------------post--------------------------------------

    def post(self):
        db, cursor = self.db_init()
        arg = parser.parse_args()     #會從client端post資料過來,轉換成dict
        account = {
            'balance':arg['balance'] or 99999,
            'account_number':arg['account_number'] or 99999,
            'user_id':arg['user_id'] or 99999,
        }
        sql = '''
            INSERT INTO `flask_schema`.`accounts` (`balance`, `account_number`, `user_id` ) 
            values ('{}', '{}', '{}');

        '''.format(account['balance'], account['account_number'], account['user_id'])
        result = cursor.execute(sql)
       
        db.commit()
        db.close()
        response = {'code':200, 'msg':'success'}
        if result == 0:
            response['msg'] = 'error'
        return jsonify(response)



#--------------------------------------------------------------------------------------------


class Account(Resource):
#-----------------------登入資料庫--------------------------------------
    def db_init(self):
        db = pymysql.connect(            #連接資料庫
            '192.168.56.103',            #資料庫所在ip
            'Neil',                      #user
            'Pn123456',                   #密碼
            'flask_schema'                #db名
        )
        cursor = db.cursor(pymysql.cursors.DictCursor)
        return db, cursor
#---------------------------get單筆資料--------------------------------------
    def get(self, id):
        db, cursor = self.db_init()
        sql = 'select * from flask_schema.accounts where id = {} and deleted != True'.format(id)
        cursor.execute(sql)
        account = cursor.fetchone()    #fetchone()只抓一筆的函式
        db.close()
        return jsonify(account)

#--------------------------update deleted-----------------------------------
#軟刪除，這邊用delete是因為要對應postman裡的方法 但在sql裡是使用update避免誤刪，其實只是在deleted欄位裡新增 1，最後在get裡加入False 或 True條件
#來避開搜尋
    def delete(self, id):
        db, cursor = self.db_init()
        sql = """UPDATE `flask_schema`.`accounts` 
        SET deleted = True
        WHERE id = {};
        """.format(id)
        result = cursor.execute(sql)
        db.commit()
        db.close()
        response = {'code':200, 'msg':'success'}
        if result == 0:
            response['msg'] = 'error'
        return jsonify(response)     

#-------------------------------update---patch--------------------------------

#postman從 body裡 form-data 更改ex:  key -> name  value -> xxx
    
    def patch(self, id):
        db, cursor = self.db_init()
        arg = parser.parse_args()     #會從client端post資料過來,轉換成dict
        account = {
            'balance':arg['balance'] or 99999,
            'account_number':arg['account_number'] or 99999,
            'user_id':arg['user_id'] or 99999,
        }

        query = []
        for key, value in account.items():   #將user轉換成tuple放入 key, value 
            if value != None:
                query.append(key + "=" + "'{}'".format(value))
        query = ",".join(query)
        
        sql = """
        UPDATE `flask_schema`.`accounts` SET {} 
        WHERE id = {};
        """.format(query, id)
        result = cursor.execute(sql)
        db.commit()
        db.close()
        response = {'code':200, 'msg':'success'}
        if result == 0:
            response['msg'] = 'error'
        return jsonify(response) 