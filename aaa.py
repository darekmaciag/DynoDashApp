import time
from w1thermsensor import W1ThermSensor
sensor1 = W1ThermSensor(sensor_id='8a1902ae86ff').get_temperature()
sensor2 = W1ThermSensor(sensor_id='8a1902c5a4ff').get_temperature()

while True:
    print(sensor1, sensor2)
    time.sleep(1)


