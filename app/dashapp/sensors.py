import time, datetime
import psycopg2
from datetime import date, datetime
import time
import json
from random import randint

import redis
from app.database import Database
import json
r=redis.Redis()

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


class Sensors:
    def __init__(self, nowstamp):
        self.testID = int(r.get("testID").decode())
        self.nowstamp = nowstamp
        self.timeconf = str(r.get("timeconf").decode())
        self.onconf = float(r.get("onconf").decode())
        self.offconf = float(r.get("offconf").decode())
        self.maxtemp = float(r.get("maxtemp").decode())
        
    def get_sensor_data(self, avgtemp, temperature1, temperature2, temperature3, temperature4, temperature5, temperature6):
        self.avgtemp = avgtemp
        self.temperature1 = temperature1
        self.temperature2 = temperature2
        self.temperature3 = temperature3
        self.temperature4 = temperature4
        self.temperature5 = temperature5
        self.temperature6 = temperature6
        with Database() as db:
            query = """ INSERT INTO sensor_data(test_id, time, timeconf, onconf, offconf, maxtemp, avg_temp, temperature1, temperature2, temperature3, temperature4, temperature5, temperature6) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING *"""
            valuses = (self.testID, self.nowstamp, self.timeconf, self.onconf, self.offconf, self.maxtemp, self.avgtemp, self.temperature1, self.temperature2, self.temperature3, self.temperature4, self.temperature5, self.temperature6)
            db.execute(query, valuses)
            db.close
            updateSensorInfo(self.testID, self.nowstamp, self.timeconf, self.onconf, self.offconf, self.maxtemp, self.avgtemp, self.temperature1, self.temperature2, self.temperature3, self.temperature4, self.temperature5, self.temperature6)


class Tests:
    def __init__(self):
        self.started = datetime.now()
        self.finished = datetime.now()

    def get_lastID(self):
        with Database() as db:
            query = """SELECT id FROM tests order by id desc limit 1"""
            data = db.query(query)
            db.close
            lastID = data[0]["id"]
            return lastID

    def create_test(self):
        self.status = False
        testid = self.get_lastID()+1
        with Database() as db:
            query = """ INSERT INTO tests(id, status, started, finished) VALUES (%s,%s,%s,%s) RETURNING *"""
            valuses = (testid, self.status, self.started, self.finished)
            db.execute(query, valuses)
            db.close
            updateTestInfo(testid, self.status, self.started, str('On air'))

    def finish_test(self):
        self.status = True
        testid = self.get_lastID()
        oldstarted = str(r.get("started").decode())
        with Database() as db:
            query = """ UPDATE tests SET status = (%s), finished = (%s) WHERE id = (%s)"""
            valuses = (self.status, self.finished, testid)
            db.execute(query, valuses)
            db.close
            updateTestInfo(testid, self.status, oldstarted, self.finished)

def updateSensorInfo(testID, nowstamp, timeconf, onconf, offconf, maxtemp, avgtemp, temperature1, temperature2, temperature3, temperature4, temperature5, temperature6):
    print("----record: ", testID, nowstamp, timeconf, onconf, offconf, maxtemp, avgtemp, temperature1, temperature2, temperature3, temperature4, temperature5, temperature6)
    r.mset({
        "testID": testID,
        "timeconf": timeconf,
        "onconf": onconf,
        "offconf": offconf,
        "maxtemp": maxtemp,
        "avgtemp": avgtemp,
        "temperature1": temperature1,
        "temperature2": temperature2,
        "temperature3": temperature3,
        "temperature4": temperature4,
        "temperature5": temperature5,
        "temperature6": temperature6,
    })


def updateTestInfo(id, status, started, finished):
    print("-------------------------")
    print("test: ",id, status, started, finished)
    print("-------------------------")
    ## Working with buffered content
    r.mset({
        "testID": id,
        "status": str(status),
        "started": str(started)[:19],
        "finished": str(finished)[:19],
    })
