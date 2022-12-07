from functools import reduce
import psutil
import json
import math
import time


priorities = {
    "low": psutil.IDLE_PRIORITY_CLASS,
    "below_normal": psutil.BELOW_NORMAL_PRIORITY_CLASS,
    "normal": psutil.NORMAL_PRIORITY_CLASS,
    "above_normal": psutil.ABOVE_NORMAL_PRIORITY_CLASS,
    "high": psutil.HIGH_PRIORITY_CLASS,
    "realtime": psutil.REALTIME_PRIORITY_CLASS
    }


f = open('config.json')
cfg = json.load(f)

intervals = [proc['interval'] for proc in cfg['processes'].values()]
startup = cfg['startupPeriod']
interval = reduce(math.gcd, intervals)
print("Interval: " + str(interval))

counter = 0

def should_change(proc):
    name = proc.name()
    if name not in cfg['processes']:
        return False
    if startup > 0:
        return True
    if cfg['processes'][name]['interval'] == 0:
        return False
    if counter % cfg['processes'][name]['interval'] != 0:
        return False
    return True

while True:
    print("counter: " + str(counter))
    for proc in psutil.process_iter():
        if not should_change(proc):
            continue
        try:
            proc.nice(priorities[cfg['processes'][proc.name()]['priority']])
            print("Set priority of " + proc.name() + " to " + cfg['processes'][proc.name()]['priority'])
        except psutil.AccessDenied:
            print("Access denied for " + proc.name())
        except psutil.NoSuchProcess:
            print("Process " + proc.name() + " no longer exists")
        except KeyError:
            print("No priority set for " + proc.name())
    
    if interval == 0:
        break

    if startup > 0:
        startup -= 2
        time.sleep(2)
        continue

    if counter == max(intervals):
        counter = 0
    else:
        counter += interval
    time.sleep(interval)