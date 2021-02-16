import time, json
import datetime
from multiprocessing import Process
from app.dashapp.sensors import Sensors
import threading
from concurrent.futures import ProcessPoolExecutor, as_completed
import redis
r=redis.Redis()

def czytaj_sensory():
    with open('outputdata.json', 'r+') as f:
            data = json.load(f)
            temperature1 = data["temperature1"]
            temperature2 = data["temperature2"]
            temperature3 = data["temperature3"]
            temperature4 = data["temperature4"]
            temperature5 = data["temperature5"]
            temperature6 = data["temperature6"]
            temperature7 = data["temperature7"]
            temperature8 = data["temperature8"]
    return temperature1, temperature2, temperature3, temperature4, temperature5, temperature6, temperature7, temperature8


def czytaj_dane():
    with open('outputdata.json', 'r+') as f:
            data = json.load(f)
            speed = data["speed"]
    x = czytaj_sensory()
    Sensors(datetime.datetime.now(),datetime.datetime.now()).get_sensor_data(speed, x[0], x[1], x[2], x[3], x[4], x[5], x[6], x[7])


def breakLoop():
    statusofloop = str(r.get("power").decode())
    if statusofloop == "off":
        return False      
    else:
        return True
        
def gettimedelta():
    timeconfig = str(r.get("timeconf").decode())
    (h, m, s) = timeconfig.split(':')
    timedelda = datetime.timedelta(hours=int(h), minutes=int(m), seconds=int(s))
    return timedelda      

        
def task2():
    timeout = gettimedelta()
    print(timeout)
    timeout_start = datetime.datetime.now()
    while True and breakLoop() and datetime.datetime.now() < timeout_start+ timeout:
        czytaj_dane()
        time.sleep(1)

def task1(task):
    executor = ProcessPoolExecutor(max_workers=1)
    executor.submit(task2)
    lewo = False
    prawo = False
    wlaczony = 0
    timeout = gettimedelta()
    timeout_start = datetime.datetime.now()
    try:
        while task == True and breakLoop() and datetime.datetime.now() < timeout_start+ timeout:
            if lewo == False and prawo == False and (wlaczony % 2) == 0 and breakLoop():
                print("zalaczam lewo")
                lewo = True
                print("lewo",lewo)
                time.sleep(float(r.get("onconf").decode()))
                lewo = False
                print("lewo", lewo)
                wlaczony += 1
                if not breakLoop():
                    break
                time.sleep(float(r.get("offconf").decode()))
            elif lewo == False and prawo == False and (wlaczony % 2) != 0 and breakLoop():
                print("zalaczam prawo")
                prawo = True
                print("prawo",prawo)
                time.sleep(float(r.get("onconf").decode()))
                prawo = False
                print("prawo", prawo)
                wlaczony += 1
                if not breakLoop():
                    break
                time.sleep(float(r.get("offconf").decode()))
            else:
                print("cos nie tak")
                prawo = False
                lewo = False
                wlaczony = 0
                break
    finally:
        print("Koniec")
        prawo = False
        lewo = False
        wlaczony = 0

# if __name__ == '__main__':
#     proc1 = Process(target=task1)
#     proc1.start()
#     proc2 = Process(target=task2)
#     proc2.start()
