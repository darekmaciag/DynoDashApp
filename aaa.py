import os
import time
 
sensorids = ["10-0008014a2604",  "10-0008014a3e9b",  "10-000801f164a6", "10-0008014a2f35",  "10-0008014a6cd3",  "28-000004bc4cae"]
sensorname = ["1", "2", "3", "4", "5", "6"]
device_file = ""
 
def read_temp_raw():
    
    
    f = open(device_file, "r")
    lines = f.readlines()
    f.close()
    return lines
 
def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != "YES":
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find("t=")
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        
        return temp_c
	
while True:
    print("Start ")
    for sensor in range(len(sensorids)):
        device_file = "/sys/bus/w1/devices/"+ sensorids[sensor] +"/w1_slave"
        temperature = (read_temp())
        print("Sensor",sensorname[sensor],)
        print(temperature)
        time.sleep(0.1)
    print(" ")
    time.sleep(1)
    