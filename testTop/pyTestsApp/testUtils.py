import epics
import unittest
from time import sleep

def waitUntilPV(namePV, expectedValue, timeout=5000, step=100):
    timePassed=0
    value = epics.caget(namePV)
    while value != expectedValue and timePassed < timeout:
        sleep(float(step)/1000)
        timePassed+=step
        value = epics.caget(namePV)
    
    return value