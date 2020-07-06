from hashlib import sha1
import hmac
from wsgiref.handlers import format_date_time
from datetime import datetime
from time import mktime
import base64
from requests import request
from pprint import pprint
import math
import json
import geocoder   #取得目前最近座標 需pip

app_id = 'FFFFFFFF-FFFF-FFFF-FFFF-FFFFFFFFFFFF'
app_key = 'FFFFFFFF-FFFF-FFFF-FFFF-FFFFFFFFFFFF'

class Auth():

    def __init__(self, app_id, app_key):
        self.app_id = app_id
        self.app_key = app_key

    def get_auth_header(self):
        xdate = format_date_time(mktime(datetime.now().timetuple()))
        hashed = hmac.new(self.app_key.encode('utf8'), ('x-date: ' + xdate).encode('utf8'), sha1)
        signature = base64.b64encode(hashed.digest()).decode()

        authorization = 'hmac username="' + self.app_id + '", ' + \
                        'algorithm="hmac-sha1", ' + \
                        'headers="x-date", ' + \
                        'signature="' + signature + '"'
        return {
            'Authorization': authorization,
            'x-date': format_date_time(mktime(datetime.now().timetuple())),
            'Accept - Encoding': 'gzip'
        }


if __name__ == '__main__':
    a = Auth(app_id, app_key)
    response = request('get', 'https://ptx.transportdata.tw/MOTC/v3/Rail/TRA/Station?$format=JSON', headers= a.get_auth_header())

loc = geocoder.ip('me').latlng  #取得座標
print(loc)

my_lat = loc[0]
my_lon = loc[1]
min_result = 9999.0
result_name = '台北'


data = json.loads(response.text)


#print(data['Stations'][0]['StationPosition'])

for i in data['Stations']:
    lat = i['StationPosition']['PositionLat']
    lon = i['StationPosition']['PositionLon']
    result = math.sqrt((lat - my_lat) ** 2 + (lon - my_lon) ** 2)  #公式
    #print(result)   #每個車站和點的距離
    if result < min_result:   #把更小的值取代min_result
        min_result = result
        result_name = i['StationName']['Zh_tw']
pprint(result_name)