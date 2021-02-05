import time, json
import datetime
from multiprocessing import Process
from sensors import JSONS, Sensors


def checkfile():
    with open('data.json', 'r+') as f:
        data = json.load(f)
    return data


def czytaj_sensory():
    data = JSONS().readjson()
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
    data = JSONS().readjson()
    speed = data["speed"]
    x = czytaj_sensory()
    Sensors(datetime.datetime.now(),datetime.datetime.now()).get_sensor_data(speed, x[0], x[1], x[2], x[3], x[4], x[5], x[6], x[7])


def breakLoop():
    statusofloop = JSONS().readconfjson()['on']
    if statusofloop == False:
        return False      
    else:
        return True
        
def gettimedelta():
    timeconfig = JSONS().readconfjson()['timeconf']
    (h, m, s) = timeconfig.split(':')
    deftimedelda = datetime.timedelta(hours=int(h), minutes=int(m), seconds=int(s))
    return deftimedelda      

        

def reading_sensors():
    timeout = gettimedelta()
    timeout_start = datetime.datetime.now()
    while True and breakLoop() and datetime.datetime.now() < timeout_start+ timeout:
        czytaj_dane()
        time.sleep(1)

def task():
    lewo = False
    prawo = False
    wlaczony = 0
    timeout = gettimedelta()
    timeout_start = datetime.datetime.now()
    try:
        while True and breakLoop() and datetime.datetime.now() < timeout_start+ timeout:
            if lewo == False and prawo == False and (wlaczony % 2) == 0 and breakLoop():
                print("zalaczam lewo")
                lewo = True
                print("lewo",lewo)
                time.sleep(JSONS().readconfjson()["onconf"])
                lewo = False
                print("lewo", lewo)
                wlaczony += 1
                if not breakLoop():
                    break
                time.sleep(JSONS().readconfjson()["offconf"])
            elif lewo == False and prawo == False and (wlaczony % 2) != 0 and breakLoop():
                print("zalaczam prawo")
                prawo = True
                print("prawo",prawo)
                time.sleep(JSONS().readconfjson()["onconf"])
                prawo = False
                print("prawo", prawo)
                wlaczony += 1
                if not breakLoop():
                    break
                time.sleep(JSONS().readconfjson()["offconf"])
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

if __name__ == '__main__':
    proc1 = Process(target=task)
    proc1.start()
    proc2 = Process(target=reading_sensors)
    proc2.start()
