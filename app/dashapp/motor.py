import time, json
import datetime
from multiprocessing import Process
from app.dashapp.sensors import Sensors
import threading
from concurrent.futures import ProcessPoolExecutor, as_completed
import redis
import RPi.GPIO as GPIO
from w1thermsensor import AsyncW1ThermSensor
import asyncio
from simple_pid import PID
import os.path

r=redis.Redis()

async def reads(aa):
    result = AsyncW1ThermSensor(sensor_id=aa)
    temp = await result.get_temperature()
    return temp
     
def average(sens_list):
    return sum(sens_list)/len(sens_list)

async def task2():
    while True:
        sens1 = asyncio.create_task(reads('0008014a2604'))
        sens2 = asyncio.create_task(reads('0008014a2f35'))
        sens3 = asyncio.create_task(reads('0008014a3e9b'))
        sens4 = asyncio.create_task(reads('0008014a6cd3'))
        sens5 = asyncio.create_task(reads('000801f164a6'))
        sens6 = asyncio.create_task(reads('000004bc4cae'))
        sensor1 = await sens1
        sensor2 = await sens2
        sensor3 = await sens3
        sensor4 = await sens4
        sensor5 = await sens5
        sensor6 = await sens6
        sens_list = [sensor1, sensor2, sensor3, sensor4, sensor5, sensor6]
        avgtemp = round(average(sens_list),3)
        await asyncio.sleep(0.1)
        Sensors(datetime.datetime.now()).get_sensor_data(avgtemp, sensor1, sensor2,sensor3,sensor4,sensor5,sensor6)

async def cycle(pin):
    GPIO.output(pin, GPIO.HIGH)
    await asyncio.sleep(float(r.get("onconf").decode()))
    GPIO.output(pin, GPIO.LOW)

async def setup(left, right):
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(left, GPIO.OUT)
    GPIO.setup(right, GPIO.OUT)

def cleanup(left, right):
    GPIO.output(left, GPIO.LOW)
    GPIO.output(right, GPIO.LOW)
    channel_used = [left, right]
    for channel in channel_used:
        GPIO.cleanup(channel)

async def task1():
    left = 5
    right = 6
    await setup(left, right)
    wlaczony = 0
    try:
        while True:
            if GPIO.input(left) == 0 and GPIO.input(right) == 0 and (wlaczony % 2) == 0:
                await cycle(left)
                wlaczony += 1
                await asyncio.sleep(float(r.get("offconf").decode()))
            elif GPIO.input(left) == 0 and GPIO.input(right) == 0 and (wlaczony % 2) != 0:
                await cycle(right)
                wlaczony += 1
                await asyncio.sleep(float(r.get("offconf").decode()))
            else:
                print("cos nie tak")
                GPIO.output(lewo, GPIO.LOW)
                GPIO.output(prawo, GPIO.LOW)
                wlaczony = 0
                break
    finally:
        print("Koniec")
        cleanup(left, right)


async def task3():
    targetT = float(r.get("maxtemp").decode())
    P = 0.01
    I = -1
    D = 1

    pid = PID(P, I, D)
    pid.setpoint = targetT
    pid.sample_time = 5
    pid.output_limits = (0.05, 10)

    while 1:
        temperature = float(r.get("avgtemp").decode())

        targetPwm = pid(temperature)
        targetPwm = round(targetPwm,2)
        print("b", targetPwm)
        r.set("onconf", targetPwm)

        await asyncio.sleep(5)