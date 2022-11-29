import time
import random
import datetime
from clickhouse_driver import Client
import os
from dotenv import find_dotenv, load_dotenv
import pymysql


load_dotenv(find_dotenv('.env'))

#随机数
def rand_str():
    return str(random.randint(1000000,2000000))

#获取当前日期时间
def get_now_time():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

#获取当前日期时间(日期)
def get_now_time_day():
    return time.strftime("%Y-%m-%d", time.localtime())


def getGroupId(datas,name):
    for data in datas:
        if name == data["name"]:
            return data["id"]
    return 0

#上月开始时间
def begin_date():
    begin_date = (datetime.datetime.now() - datetime.timedelta(days=30)).strftime("%Y-%m-%d")
    begin_date = datetime.datetime.strptime(begin_date, "%Y-%m-%d")
    return str(begin_date)
#本月结束时间
def end_date():
    end_date = datetime.datetime.strptime(time.strftime('%Y-%m-%d', time.localtime(time.time())), "%Y-%m-%d")
    return str(end_date)

#上月开始时间
def begin_date_today():
    end_date = datetime.datetime.strptime(time.strftime('%Y-%m-%d', time.localtime(time.time())), "%Y-%m-%d")
    return str(end_date)
#本月结束时间
def end_date_today():
    begin_date = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    begin_date = datetime.datetime.strptime(begin_date, "%Y-%m-%d")
    return str(begin_date)

#sleep
def sleep(n_secs):
    time.sleep(n_secs)

def data_len(data):
    return len(data)
#=========================================CK===================================================

#连接CK
def connect_ck():
    host = os.environ.get("CLICKHOUSE_HOST")
    port = os.environ.get("CLICKHOUSE_PORT")
    user = os.environ.get("CLICKHOUSE_USERNAME")
    password = os.environ.get("CLICKHOUSE_PASSWD")
    client = Client(host=host, database='default', user=user, password=password, send_receive_timeout=30,
                    port=port)

    return client

#=========================================CK===================================================


#=========================================MYSQL================================================
#连接mysql
def connect_mysql(db):
    host = os.environ.get("MYSQL_HOST")
    port = int(os.environ.get("MYSQL_PORT"))
    username = os.environ.get("MYSQL_USERNAME")
    passwd = os.environ.get("MYSQL_PASSWD")
    conn = pymysql.connect(host=host, port=port, user=username, passwd=passwd, db=db)

    return conn


#=========================================MYSQL================================================



#=========================================assert================================================

#设备类型分布
def assert_type_percentage(sensorTypeData):
    conn = connect_mysql("iot-sensor")
    cur = conn.cursor()

    cur.execute(r"SELECT * FROM sensor_type_percentage")
    mysql_datas = []
    for r in cur:
        mysql_datas.append(r)
    if len(mysql_datas) != len(sensorTypeData):
        cur.close()
        conn.close()
        return "fail"
    for data in mysql_datas:
        if data[2] not in str(sensorTypeData):
            cur.close()
            conn.close()
            return "fail"
        else:
            for sensortype in sensorTypeData:
                if data[2] == sensortype["sensorTypeName"]:
                    if data[4] != sensortype["sensorCount"]:
                        print(data)
                        print(sensortype)
                        cur.close()
                        conn.close()
                        return "fail"
    cur.close()
    conn.close()
    return "success"


#=========================================assert================================================