from binance import BinanceSocketManager
from binance.client import Client
import requests
import json
import time
import datetime


series_id = ['CUSR0000SA0']         # квадратные скобки не убирать
url = 'https://api.bls.gov/publicAPI/v2/timeseries/data/'
headers = {'Content-type': 'application/json'}
data = json.dumps({"seriesid": series_id, "startyear": 2023, "endyear": 2023, "registrationkey": "b82e772a2a39482e9540ed84f37ba9e6"})

period = 'M13'

'   # что ищём
X = 298.112         # с чем сравниваем

# timestamp = datetime.datetime(2023, 1, 23, 8, 0, 0)  # 2023 год, 23 января, 8:00:00
timestamp = 1673989070   # время в unix-формате
timestamp_period = 3*60  # 3 минуты = 3*60 секунд. сколько будет ждать появления данных

# Binance
api_key = 'aeTRWRdLrGe0IYheWIIjTURntYu2nSpBeVnHXPjrF1og9ilBH2sbaNw1fo2khtif'
secret_key= 'Kp9BeIhTqdpzJJgAaE7pPGHh6fAnevdDGozXJYW3CLpYqD8h8YgqAbYmRK3CwaCw'

timeInForce = 'GTC'
recvwindow = 3000


def parse(my_period):
    response = requests.post(url, headers=headers, data=data)
    json_data = json.loads(response.text)
    time = json_data['responseTime']
    status = json_data['status']
    if status == 'REQUEST_FAILED':
        return time
    results = json_data['Results']
    if results == None:
        return time
    my_objects = results.get('series')
    if my_objects == None:
        return time
    my_object = my_objects[0]
    if my_object == None:
        return time
    data_all = my_object.get('data')
    if data_all == None:
        return time
    data = data_all[0]
    if data == None:
        return time
    period = data.get('period')
    if period != my_period:
        return time
    value = data.get('value')
    if value == None:
        return time
    return time, value    


def main_parse():
    global X
    global period
    t1 = time.perf_counter()
    for i in range(timestamp_period * 5):   # timestamp * 1000 / 200
        data = parse(period)
        if type(data) == tuple:
            break
        if data > 200:
            continue
        sleep_time = (200 - data) * 0.001
        time.sleep(sleep_time)
    else:
        print('За заданное время value не найдено.')
        return
    t2 = time.perf_counter()
    time, value = data
    t3 = time.perf_counter()
    if value > X:
        t4 = time.perf_counter()
        binance_register("AAVEUSDT",'SELL', 0.1)
        t5 = time.perf_counter()
    elif value < X:
        t4 = time.perf_counter()
        binance_register("AAVEUSDT",'BUY', 0.1)
        t5 = time.perf_counter()
    else:
        t4 = time.perf_counter()
        return t2-t1, t3-t4
    return t2-t1, t3-t4, t4-t5


def binance_register(coin, side, trade_quantity):
    client = Client(api_key, secret_key)
    bm = BinanceSocketManager(client)
    ts = bm.trade_socket(coin)
    client.futures_create_order(symbol=coin, side=side, type='MARKET', quantity=trade_quantity,
                                timeInForce=timeInForce, timestamp=int(time.mktime(datetime.datetime.today().timetuple())), recvwindow=recvwindow)


def main():
    global timestamp
    now = time.mktime(datetime.datetime.today().timetuple()) # datetime.datetime.today()
    seconds_till_start = timestamp - now
    time.sleep(seconds_till_start)
    time_ = main_parse()
    if time_:
        for i, val in enumerate(time_):
            print(f'Часть {i+1} выполнена за {val} секунд.')


if __name__ == '__main__':
    main()
