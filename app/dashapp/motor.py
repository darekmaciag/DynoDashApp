import time, json
import datetime
from multiprocessing import Process
from app.dashapp.sensors import Sensors
import threading
from concurrent.futures import ProcessPoolExecutor, as_completed
import redis
import RPi.GPIO as GPIO
from w1thermsensor import W1ThermSensor

r=redis.Redis()

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
        sensor1 = W1ThermSensor(sensor_id='8a1902ae86ff').get_temperature()
        sensor2 = W1ThermSensor(sensor_id='8a1902c5a4ff').get_temperature()
        Sensors(datetime.datetime.now()).get_sensor_data(1, sensor1, sensor2,3,4,5,6,7,8)
        time.sleep(1)

def task1(task):
    executor = ProcessPoolExecutor(max_workers=1)
    executor.submit(task2)
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    k1 = 20
    k2 = 21
    lewo = False
    prawo = False
    wlaczony = 0
    timeout = gettimedelta()
    timeout_start = datetime.datetime.now()
    try:
        GPIO.setup(k1, GPIO.OUT)
        GPIO.setup(k2, GPIO.OUT)
        while task == True and breakLoop() and datetime.datetime.now() < timeout_start+ timeout:
            if lewo == False and prawo == False and (wlaczony % 2) == 0 and breakLoop():
                print("zalaczam lewo")
                lewo = True
                GPIO.output(k1, GPIO.HIGH)
                time.sleep(float(r.get("onconf").decode()))
                lewo = False
                GPIO.output(k1, GPIO.LOW)
                wlaczony += 1
                if not breakLoop():
                    break
                time.sleep(float(r.get("offconf").decode()))
            elif lewo == False and prawo == False and (wlaczony % 2) != 0 and breakLoop():
                print("zalaczam prawo")
                prawo = True
                GPIO.output(k2, GPIO.HIGH)
                time.sleep(float(r.get("onconf").decode()))
                prawo = False
                GPIO.output(k2, GPIO.LOW)
                wlaczony += 1
                if not breakLoop():
                    break
                time.sleep(float(r.get("offconf").decode()))
            else:
                print("cos nie tak")
                prawo = False
                lewo = False
                GPIO.output(k1, GPIO.LOW)
                GPIO.output(k2, GPIO.LOW)
                wlaczony = 0
                break
    finally:
        print("Koniec")
        prawo = False
        lewo = False
        GPIO.output(k1, GPIO.LOW)
        GPIO.output(k2, GPIO.LOW)
        channel_used = [20, 21]
        for channel in channel_used:
            GPIO.cleanup(channel)
        wlaczony = 0

# if __name__ == '__main__':
#     proc1 = Process(target=task1)
#     proc1.start()
#     proc2 = Process(target=task2)
#     proc2.start()
