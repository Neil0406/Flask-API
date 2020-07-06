from flask import jsonify, make_response      
from flask_restful import  Api, Resource, reqparse
import pymysql

parser = reqparse.RequestParser()   #post
parser.add_argument('name')
parser.add_argument('gender')
parser.add_argument('birth')
parser.add_argument('note')



class Users(Resource):
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
        sql = 'select * from flask_schema.users Where deleted != False;'
        cursor.execute(sql)
        users = cursor.fetchall()          #fetchall() 抓全部
        db.close()
        return jsonify(users)          # 以json格式顯示，需要import

#---------------------------post--------------------------------------

    def post(self):
        db, cursor = self.db_init()
        arg = parser.parse_args()     #會從client端post資料過來,轉換成dict
        user = {
            'name':arg['name'],
            'gender':arg['gender'],
            'birth':arg['birth'] or '1990-01-01',
            'note':arg['note']
        }
        sql = '''
            INSERT INTO `flask_schema`.`users` (`name`, `gender`, `birth`, `note`) 
            values ('{}', '{}', '{}', '{}');

        '''.format(user['name'], user['gender'], user['birth'], user['note'])
        result = cursor.execute(sql)
       
        db.commit()
        db.close()
        response = {'msg':'success'}
        code = 201                             #驗證授權，若不設定預設是200
        if result == 0:                        #201是更明確的讓使用者知道成功建立使用者
            response['msg'] = 'error'
            code = 400                            #驗證授權
        return make_response(jsonify(response), 201) 
class User(Resource):
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
        sql = 'select * from flask_schema.users where id = {}'.format(id)
        cursor.execute(sql)
        user = cursor.fetchone()    #fetchone()只抓一筆的函式
        db.close()
        return jsonify(user)

#--------------------------update deleted----------------------------------------
#軟刪除，這邊用delete是因為要對應postman裡的方法 但在sql裡是使用update避免誤刪，其實只是在deleted欄位裡新增 1，最後在get裡加入False 或 True條件
#來避開搜尋
    def delete(self, id):
        db, cursor = self.db_init()
        sql = """UPDATE `flask_schema`.`users` 
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
        user = {
            'name':arg['name'],
            'gender':arg['gender'],
            'birth':arg['birth'] or '1990-01-01',
            'note':arg['note']
        }

        query = []
        for key, value in user.items():   #將user轉換成tuple放入 key, value 
            if value != None:
                query.append(key + "=" + "'{}'".format(value))
        query = ",".join(query)
        
        sql = """
        UPDATE `flask_schema`.`users` SET {} 
        WHERE id = {};
        """.format(query, id)
        result = cursor.execute(sql)
        db.commit()
        db.close()
        response = {'code':200, 'msg':'success'}
        if result == 0:
            response['msg'] = 'error'
        return jsonify(response) 
