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

#查询设备数量
def sensor(type):
    ck = connect_ck()
    sql = r"SELECT count( 1 ) AS sensorSum, count( CASE WHEN ( expired_time < '2000-01-01' ) THEN 1 ELSE NULL END ) AS inactivatedNum, count( CASE WHEN (( expired_time > '2000-01-01' ) AND ( expired_time < now())) THEN 1 ELSE NULL END ) AS offline, count( CASE WHEN ( expired_time > now()) THEN 1 ELSE NULL END ) AS ONLINE FROM sensor_all_info final WHERE deleted =0"
    res = ck.execute(sql)
    ck.disconnect()
    # 设备总量
    if type == 0:
        return res[0][0]
    # 未激活
    if type == 1:
        return res[0][1]
    # 离线
    if type == 2:
        return res[0][2]
    # 在线
    if type == 3:
        return res[0][3]
    return


#接入日志总数
def sensor_log_total():
    ck = connect_ck()
    sql = r"select sum(window_count) from sensor_sum final"
    res = ck.execute(sql)
    ck.disconnect()
    return round(res[0][0]/10000,4)



#今日接入日志数
def sensor_log_total_today():
    ck = connect_ck()
    sql = r"select sum(window_count) from sensor_sum final where p_date = today()"
    res = ck.execute(sql)
    ck.disconnect()
    return res[0][0]

#接入设备总数
def sensor_info_total():
    ck = connect_ck()
    sql = r"select count(1) from sensor_all_info final where deleted = 0;"
    res = ck.execute(sql)
    ck.disconnect()
    return res[0][0]

#今日接入设备数
def sensor_info_total_today():
    ck = connect_ck()
    sql = r"select count(*) from sensor_all_info where create_time >= '" + begin_date_today() + "' and create_time <= '" + end_date_today() + "'  and deleted  = 0"
    res = ck.execute(sql)
    ck.disconnect()
    return res[0][0]

#今日接入设备种类
def sensor_type_total_today():
    ck = connect_ck()
    sql = r"select type_code from sensor_all_info where create_time >= '" + begin_date_today() + "' and create_time <= '" + end_date_today() + "'  and deleted  = 0 group by type_code"

    res = ck.execute(sql)
    ck.disconnect()
    return len(res)




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

#获取设备类型数量
def get_sensorType_total():
    conn = connect_mysql("iot-sensor")
    cur = conn.cursor()
    cur.execute(r"SELECT count(*) FROM sensor_type_percentage")
    res_arr = []
    for r in cur:
        res_arr.append(r)
    cur.close()
    conn.close()
    return res_arr[0][0]

#获取物模型数量
def model_total():
    conn = connect_mysql("iot-sensor")
    cur = conn.cursor()
    cur.execute(r"SELECT count(*) FROM physical_model_info where deleted = 0")
    res_arr = []
    for r in cur:
        res_arr.append(r)
    cur.close()
    conn.close()
    return res_arr[0][0]


#今日新增事件1
def eventTodayTotal():
    conn = connect_mysql("iot-scene")
    cur = conn.cursor()
    cur.execute(r"SELECT count(*) FROM event_info_message where create_time > DATE_FORMAT(NOW(),'%Y-%m-%d 00:00:00') and create_time <DATE_FORMAT(NOW(),'%Y-%m-%d 23:59:59')")
    res_arr = []
    for r in cur:
        res_arr.append(r)
    cur.close()
    conn.close()
    return res_arr[0][0]

#发现事件总数1
def eventTotal():
    conn = connect_mysql("iot-scene")
    cur = conn.cursor()
    cur.execute(r"SELECT count(*) FROM event_info_message")
    res_arr = []
    for r in cur:
        res_arr.append(r)
    cur.close()
    conn.close()
    return res_arr[0][0]

#今日新增算法 1
def ruleTodayTotal():
    conn = connect_mysql("iot-scene")
    cur = conn.cursor()
    cur.execute(r"SELECT count(*) FROM event_info where deleted = 0 and event_status = 2 and create_time > DATE_FORMAT(NOW(),'%Y-%m-%d 00:00:00') and create_time <DATE_FORMAT(NOW(),'%Y-%m-%d 23:59:59')")
    res_arr = []
    for r in cur:
        res_arr.append(r)
    cur.close()
    conn.close()
    return res_arr[0][0]

#运行算法总个数 1
def ruleTotal():
    conn = connect_mysql("iot-scene")
    cur = conn.cursor()
    cur.execute(r"SELECT count(*) FROM event_info where deleted = 0 and event_status = 2")
    res_arr = []
    for r in cur:
        res_arr.append(r)
    cur.close()
    conn.close()
    return res_arr[0][0]

#一般事件
def statisticsByLevel_1_3():
    conn = connect_mysql("iot-scene")
    cur = conn.cursor()
    cur.execute(r"SELECT count(*) FROM event_info_message where deleted = 0 and event_level_name = 'I级' or event_level_name = 'II级' or event_level_name = 'III级'")
    res_arr = []
    for r in cur:
        res_arr.append(r)
    cur.close()
    conn.close()
    return res_arr[0][0]

#告警事件
def statisticsByLevel_4_5():
    conn = connect_mysql("iot-scene")
    cur = conn.cursor()
    cur.execute(
        r"SELECT count(*) FROM event_info_message where deleted = 0 and event_level_name = 'IV级' or event_level_name = 'V级'")
    res_arr = []
    for r in cur:
        res_arr.append(r)
    cur.close()
    conn.close()
    return res_arr[0][0]
#重大事件
def statisticsByLevel_warning():
    conn = connect_mysql("iot-scene")
    cur = conn.cursor()
    cur.execute(
        r"SELECT count(*) FROM event_info_message where deleted = 0 and event_level_name = '告警'")
    res_arr = []
    for r in cur:
        res_arr.append(r)
    cur.close()
    conn.close()
    return res_arr[0][0]

#已流转事件数
def message_count():
    conn = connect_mysql("iot-scene")
    cur = conn.cursor()
    cur.execute(r"SELECT count(*) FROM info_message")
    res_arr = []
    for r in cur:
        res_arr.append(r)
    cur.close()
    conn.close()
    return res_arr[0][0]
#已完成事件数
def message_end():
    conn = connect_mysql("iot-scene")
    cur = conn.cursor()
    cur.execute(r"SELECT count(*) FROM info_message where status = 2")
    res_arr = []
    for r in cur:
        res_arr.append(r)
    cur.close()
    conn.close()
    return res_arr[0][0]
#未完成事件数
def message_start():
    conn = connect_mysql("iot-scene")
    cur = conn.cursor()
    cur.execute(r"SELECT count(*) FROM info_message where status = 1")
    res_arr = []
    for r in cur:
        res_arr.append(r)
    cur.close()
    conn.close()
    return res_arr[0][0]

#数据流转次数
def shareData_totalTimes():
    conn = connect_mysql("iot-share")
    cur = conn.cursor()
    cur.execute(r"SELECT count(*) FROM task_info WHERE deleted = 0")
    res_arr = []
    for r in cur:
        res_arr.append(r)
    cur.close()
    conn.close()
    print(res_arr[0][0])
    return res_arr[0][0]

#数据流转总流量
def shareData_totalNum():
    conn = connect_mysql("iot-share")
    cur = conn.cursor()
    cur.execute(r"SELECT SUM(share_data_num) FROM task_info WHERE deleted = 0")
    res_arr = []
    for r in cur:
        res_arr.append(r)
    cur.close()
    conn.close()
    print(float(res_arr[0][0]/10000))
    return float(res_arr[0][0]/10000)

#设备、日志数据共享   business_type: 1是设备 2是日志
def share_total(business_type):
    conn = connect_mysql("iot-share")
    cur = conn.cursor()
    cur.execute(r"select SUM(share_data_num) share_data_num from task_info  where deleted = 0 and business_type = " + str(business_type) +" GROUP BY business_type")
    res_arr = []
    for r in cur:
        res_arr.append(r)
    cur.close()
    conn.close()
    return res_arr[0][0]

#今日设备、日志数据共享   business_type: 1是设备 2是日志
def share_total_today(business_type):
    conn = connect_mysql("iot-share")
    cur = conn.cursor()
    if business_type == 1:
        cur.execute(r"select sum(num) from sensor_statistic where time = '" + get_now_time_day() + "' and deleted = 0")
    if business_type == 2:
        cur.execute(r"select IFNULL(sum(num),0) from sensor_log_statistic where time = '" + get_now_time_day() + "' and deleted = 0")
    res_arr = []
    for r in cur:
        res_arr.append(r)
    cur.close()
    conn.close()
    return res_arr[0][0]

#设备共享任务总数 business_type: 1是设备 2是日志
def task_info_total(business_type):
    conn = connect_mysql("iot-share")
    cur = conn.cursor()
    cur.execute(r"SELECT count(*) FROM task_info where deleted = 0 and business_type = " + str(business_type))
    res_arr = []
    for r in cur:
        res_arr.append(r)
    cur.close()
    conn.close()
    return res_arr[0][0]


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