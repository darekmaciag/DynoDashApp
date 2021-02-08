import time, datetime
import psycopg2
from datetime import date, datetime
import time
import json
from random import randint
from app.database import Database
import json


class Semaphore:
    def __init__(self, filename='test.txt'):
        self.filename = filename
        with open(self.filename, 'w') as f:
            f.write('done')

    def lock(self):
        with open(self.filename, 'w') as f:
            f.write('working')

    def unlock(self):
        with open(self.filename, 'w') as f:
            f.write('done')

    def is_locked(self):
        return open(self.filename, 'r').read() == 'working'


class JSONS:
    def __init__(self):
        self.open = open('data.json', 'r+')
        self.confj = open('confdata.json', 'r+')
        self.testj = open('testdata.json', 'r+')
        self.outputj = open('outputdata.json', 'r+')

    def readjson(self):
        data = json.load(self.open)
        return data

    def readconfjson(self):
        data = json.load(self.confj)
        return data

    def readtestjson(self):
        data = json.load(self.testj)
        return data

    def readoutputjson(self):
        data = json.load(self.outputj)
        return data
    
    def writestatus(self, row, value):
        data = json.load(self.confj)
        data[row] = value # <--- add `id` value.
        self.confj.seek(0)        # <--- should reset file position to the beginning.
        json.dump(data, self.confj, indent=4)
        self.confj.truncate()


class Sensors:
    def __init__(self, nowstamp, aa):
        testdata = JSONS().readtestjson()
        self.testID = testdata['testID']
        self.nowstamp = nowstamp
        self.timeconf = aa
        confdata = JSONS().readconfjson()
        self.onconf = confdata['onconf']
        self.offconf = confdata['offconf']

    def get_sensor_data(self, speed, temperature1, temperature2, temperature3, temperature4, temperature5, temperature6, temperature7, temperature8, ):
        self.speed = speed
        self.temperature1 = temperature1
        self.temperature2 = temperature2
        self.temperature3 = temperature3
        self.temperature4 = temperature4
        self.temperature5 = temperature5
        self.temperature6 = temperature6
        self.temperature7 = temperature7
        self.temperature8 = temperature8
        with Database() as db:
            query = """ INSERT INTO sensor_data(test_id, time, timeconf, onconf, offconf, speed, sensor_id, temperature) VALUES (%s,%s,%s,%s,%s,%s,%s,%s) RETURNING *"""
            valuses = (self.testID, self.nowstamp, self.timeconf, self.onconf, self.offconf, self.speed, 1, self.temperature1)
            db.execute(query, valuses)
            db.close
            updateSensorInfo(self.testID, self.timeconf, self.onconf, self.offconf, self.speed, self.temperature1, self.temperature2, self.temperature3, self.temperature4, self.temperature5, self.temperature6, self.temperature7, self.temperature8)


class Tests:
    def __init__(self):
        self.started = datetime.now()
        self.finished = datetime.now()

    def create_test(self):
        self.status = False
        testid = JSONS().readtestjson()['testID'] + 1
        with Database() as db:
            query = """ INSERT INTO tests(id, status, started, finished) VALUES (%s,%s,%s,%s) RETURNING *"""
            valuses = (testid, self.status, self.started, self.finished)
            db.execute(query, valuses)
            db.close
            updateTestInfo(testid, self.status, self.started, self.finished)


    def finish_test(self):
        self.status = True
        data = JSONS().readtestjson()
        testid = data['testID']
        oldstarted = data['started'] # <--- add `id` value.
        with Database() as db:
            query = """ UPDATE tests SET status = (%s), finished = (%s) WHERE id = (%s)"""
            valuses = (self.status, self.finished, testid)
            db.execute(query, valuses)
            db.close
            updateTestInfo(testid, self.status, oldstarted, self.finished)


def updateSensorInfo(testID, timeconf, onconf, offconf, speed, temperature1, temperature2, temperature3, temperature4, temperature5, temperature6, temperature7, temperature8):
    jsonFile = open("outputdata.json", "r") # Open the JSON file for reading
    data = json.load(jsonFile) # Read the JSON into the buffer
    jsonFile.close() # Close the JSON file
    print("----record: ", testID, timeconf, onconf, offconf, speed, temperature1, temperature2, temperature3, temperature4, temperature5, temperature6, temperature7, temperature8)

    ## Working with buffered content
    data['testID'] = testID
    data["timeconf"] = str(timeconf)
    data["onconf"] = onconf
    data["offconf"] = offconf
    data["speed"] = speed
    data["temperature1"] = temperature1
    data["temperature2"] = temperature2
    data["temperature3"] = temperature3
    data["temperature4"] = temperature4
    data["temperature5"] = temperature5
    data["temperature6"] = temperature6
    data["temperature7"] = temperature7
    data["temperature8"] = temperature8

    ## Save our changes to JSON file
    jsonFile = open("outputdata.json", "w+")
    jsonFile.write(json.dumps(data, indent=4))
    jsonFile.close()

def updateTestInfo(id, status, started, finished):
    jsonFile = open("testdata.json", "r") # Open the JSON file for reading
    data = json.load(jsonFile) # Read the JSON into the buffer
    jsonFile.close() # Close the JSON file
    print("-------------------------")
    print("test: ",id, status, started, finished)
    print("-------------------------")

    ## Working with buffered content
    data['testID'] = id
    data["status"] = status
    data["started"] = str(started)
    data["finished"] = str(finished)

    ## Save our changes to JSON file
    jsonFile = open("testdata.json", "w+")
    jsonFile.write(json.dumps(data, indent=4))
    jsonFile.close()



# Tests().create_test(True)
# time.sleep(1)
# Tests().finish_test(False)
# aa = datetime.now()
# Sensors(datetime.now(),aa).get_sensor_data(1,1,1,1,1,1,1,1,1)