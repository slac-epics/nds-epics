#!/usr/bin/env python
import sys
import os
import unittest
import epics
from epics import ca
import subprocess
from time import sleep
import iocControl
from iocControl import printv
from parametrizedTestCase import ParametrizedTestCase
import ioctests
from testUtils import waitUntilPV




def handle_messages(text):
    pass

class TestNdsError(ParametrizedTestCase):
    '''Testing basic load and initialization of NDS driver in EPICS'''
    ''' 1-setup
    2-test***
    3-tearDown
    '''

    prefix =""
    ioc= None
    UNKNOWN = 0
    OFF = 1
    SWITCH_OFF = 2
    INITIALIZING = 3
    ON = 4
    STOPPING = 5
    STARTING = 6
    RUNNING = 7
    FAULT = 8

    line = "+---------------------------------------------------------------------"

    sm_dic={UNKNOWN:'UNKNOWN',OFF:'OFF',SWITCH_OFF:'SWITCH_OFF',INITIALIZING:'INITIALIZING',ON:'ON',STOPPING:'STOPPING',STARTING:'STARTING',RUNNING:'RUNNING', FAULT:'FAULT',None:'NONE'}

    def setUp(self):
        try:
            ioctests.setup()
            ca.initialize_libca()
            epics.ca.replace_printf_handler(handle_messages)
            self.ioc = iocControl.iocControl()
            self.ioc.startIOC() 

            appName = 'ndsex1'
            libFile = 'libnds3-DeviceError.so' 
            subsFile = 'DeviceError.substitutions'
            DeviceName = "B-0"
            DriverName = "DeviceError"

            iocCmd =  self.ioc.iocCommandCompose(appName, libFile,subsFile,DeviceName,DriverName,self.param)
            #print("")
            #print(iocCmd) 

            self.ioc.iocProcess.stdin.write(iocCmd)
            sleep(2)
            print(self.line)
            print("|")
            print("|                    TEST NDSError")
            print("|")
            print(self.line)    
            print("|")


            CBS1 = 'TEST'
            CBS2 = 'FCT0'
            BOARDTYPE = 'B'
            BOARDTYPEIDX='0'
            DEVICE_NAME = 'DeviceError'


            self.prefix = CBS1+'-'+CBS2\
                +'-HWCF:'+BOARDTYPE+'-'+BOARDTYPEIDX+'-'+DEVICE_NAME    

        except KeyboardInterrupt:
            print("KeyboardInterrupt. Finalizing.")
            if self.ioc is not None:
                self.ioc.stop()
        except: 
            print("got an exception")
            if self.ioc is not None:
                self.ioc.stop()
            raise


    def tearDown(self):
        ca.finalize_libca()
        if self.ioc is not None:
            self.ioc.stop()

    def testState(self):
        OKGREEN = '\033[92m'
        FAIL = '\033[91m'
        ENDC = '\033[0m'
        FAIL_MSG = FAIL+"    [FAILED]"+ENDC
        OK_MSG = "|"+OKGREEN+"   [OK]"+ENDC+"\n\n"

        epics.ca.replace_printf_handler(handle_messages)
        #space = "    "
        intro = "|---"
        space = "|   "

        SUCCESS=0
        TIMEOUT=10
        HWLIMIT=11
        COMM=9
        DISABLE=18
        WRITE=2
        READ=1


        errorVal2Stat = {
            0:SUCCESS,
            1:TIMEOUT,
            2:HWLIMIT,
            3:COMM,
            4:DISABLE,
            5:WRITE
            }
        errorVal2Stat2 = {
            0:SUCCESS,
            1:TIMEOUT,
            2:HWLIMIT,
            3:COMM,
            4:DISABLE,
            5:READ
            }

        valueError=[0,1,2,3,4,5]
        typeError=["SUCCESS", "TIMEOUT", "HWLIMIT", "COMM", "DISABLE", "WRITE"]   
        typeError2=["SUCCESS", "TIMEOUT", "HWLIMIT", "COMM", "DISABLE", "READ"]  

        try: 
            for value in valueError:
                nameS = self.prefix+"-delegateOutError"
                epics.caput(nameS,value,wait= False,timeout=5)
                res = waitUntilPV(nameS,value)
                print(space+nameS+": "+str(res))
                self.assertEqual(res,value,FAIL_MSG)
                error = waitUntilPV(nameS + ".STAT", errorVal2Stat[value])

                self.assertEqual(error,errorVal2Stat[value],FAIL_MSG)
                print(typeError[value])
                print(OK_MSG)
                sleep(1)


        except KeyboardInterrupt:
            print("KeyboardInterrupt")
            self.ioc.stop()
            ioc = None
            print("Asserting False-Test interrupted manually")
            self.assertEqual(1,0)
        
        
        try:
            for value in valueError:
                nameS = self.prefix+"-variableOutError"
                epics.caput(nameS,value,wait= False,timeout=5)
                res =  waitUntilPV(nameS,value)
                self.assertEqual(res,value,FAIL_MSG)
                nameS2 = self.prefix+"-delegateInError"
                print(space+nameS+": "+str(res))
                error = waitUntilPV(nameS2 + ".STAT",errorVal2Stat2[value])
                self.assertEqual(error,errorVal2Stat2[value],FAIL_MSG)
                print(typeError2[value])
                print(OK_MSG)
                sleep(1)

        except KeyboardInterrupt:
            print("KeyboardInterrupt")
            self.ioc.stop()
            ioc = None
            print("Asserting False-Test interrupted manually")
            self.assertEqual(1,0)
