from time import time

def pause(secs):
    init_time = time()
    while time() < init_time+secs: pass

print("See ya in 10 seconds")
pause(10)
print("Heeeeeelooooo there")