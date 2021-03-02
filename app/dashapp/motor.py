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

r=redis.Redis()
     
async def task2():
    while True:
        sensor1 = await AsyncW1ThermSensor(sensor_id='8a1902ae86ff').get_temperature()
        sensor2 = await AsyncW1ThermSensor(sensor_id='8a1902c5a4ff').get_temperature()
        print(sensor2, sensor1)
        await asyncio.sleep(1)
        Sensors(datetime.datetime.now()).get_sensor_data(1, sensor1, sensor2,3,4,5,6,7,8)

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
    left = 20
    right = 21
    await setup(left, right)
    wlaczony = 0
    try:
        while True:
            if GPIO.input(left) == 0 and GPIO.input(right) == 0 and (wlaczony % 2) == 0:
                print("zalaczam lewo")
                await cycle(left)
                wlaczony += 1
                await asyncio.sleep(float(r.get("offconf").decode()))
            elif GPIO.input(left) == 0 and GPIO.input(right) == 0 and (wlaczony % 2) != 0:
                print("zalaczam lewo")
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
    pass