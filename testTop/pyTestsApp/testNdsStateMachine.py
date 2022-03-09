#!/usr/bin/env python
import unittest
import epics
from epics import ca
import subprocess
from testUtils import waitUntilPV
from time import sleep
import iocControl
from iocControl import printv
import ioctests
from parametrizedTestCase import ParametrizedTestCase

def handle_messages(text):
    pass

class TestNdsStateMachine(ParametrizedTestCase):
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
            #epics.ca.replace_printf_handler(handle_messages)
            self.ioc = iocControl.iocControl()
            self.ioc.startIOC() 
            
            appName = 'ndsex1'
            libFile = 'libnds3-DeviceStateMachine.so' 
            subsFile = 'StateMachine.substitutions'
            DeviceName = "B-0"
            DriverName = "DeviceStateMachine"
            # if(self.param == "INIT=YES"):
            #      DeviceName = "B-1"
            #      subsFile = 'StateMachine2.substitutions'
            iocCmd =  self.ioc.iocCommandCompose(appName, libFile,subsFile,DeviceName,DriverName,self.param)
            #print("")
            #print(iocCmd) 
            
            self.ioc.iocProcess.stdin.write(iocCmd)
            sleep(2)
            print(self.line)
            print("|")
            print("|                    TEST STATE MACHINE NODE")
            print("|")
            print(self.line)    
            print("|")
            printv("| Test transitions of states using Python channel access",1)
            if(self.param == "INIT=YES"):
                printv("| Initialization no RBV",1)       
            printv("|\n"+self.line,1)

            CBS1 = 'TEST'
            CBS2 = 'FCT0'
            BOARDTYPE = 'B'
            BOARDTYPEIDX='0'
            STATEMACHINE_NAME = 'StateMachine'
            # if(self.param == "INIT=YES"):
            #     BOARDTYPEIDX='1'

            self.prefix = CBS1+'-'+CBS2\
                +'-HWCF:'+BOARDTYPE+'-'+BOARDTYPEIDX+'-'+STATEMACHINE_NAME    
           
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
        #epics.ca.replace_printf_handler(handle_messages)
        #space = "    "
        intro = "|---"
        space = "|   "
        try:   
            sleep(1)
            nameG = self.prefix+'-getState'
            nameS = self.prefix + '-setState'
            nameGG = self.prefix + '-getGlobalState'
            
            '''Default State'''
            print("|---Default State")
            
            value = waitUntilPV(nameG, self.OFF)
            print(space+nameG+": "+self.sm_dic.setdefault(value,None))

            self.assertEqual(value,self.OFF,FAIL_MSG)
            print(OK_MSG)
            

            #''' Default Global '''
            #print(intro+"Default Global State")
            #value =  epics.caget(nameGG)
            #print(space+nameGG+": "+self.sm_dic.setdefault(value,None))

            #self.assertEqual(value,self.OFF,FAIL_MSG)
            #print(OK_MSG)


            '''OFF --> ON'''
            print(intro+"OFF --> ON")
            epics.caput(nameS,self.ON,wait= False,timeout=5)
            value = waitUntilPV(nameG, self.ON)

#            value =  epics.caget(nameG)
            print(space+nameG+": "+self.sm_dic.setdefault(value,None))
            
            self.assertEqual(value,self.ON,FAIL_MSG)
            
            print(OK_MSG)

            #'''Global ON'''
            #print(intro+"Global ON")
            
            #value =  epics.caget(nameGG)
            #print(space+nameGG+": "+self.sm_dic.setdefault(value,None))

            #self.assertEqual(value,self.ON,FAIL_MSG)
            #print(OK_MSG)


            '''ON --> RUNNING'''
            print(intro+"ON --> RUNNING")
            epics.caput(nameS,self.RUNNING,wait= False,timeout=5)
            value = waitUntilPV(nameG, self.RUNNING)

            print(space+nameG+": "+self.sm_dic.setdefault(value,None))
            
            self.assertEqual(value,self.RUNNING,FAIL_MSG)
            print(OK_MSG)

            #'''Global RUNNING'''
            #print(intro+"Global RUNNING")
            #value =  epics.caget(nameGG)
            #print(space+nameGG+": "+self.sm_dic.setdefault(value,None))

            #self.assertEqual(value,self.RUNNING,FAIL_MSG)
            #print(OK_MSG)


            '''RUNNING --> ON'''
            print(intro+"RUNNING --> ON")
            epics.caput(nameS,self.ON,wait= False,timeout=5)
            value = waitUntilPV(nameG, self.ON)

            print(space+nameG+": "+self.sm_dic.setdefault(value,None))
            
            self.assertEqual(value,self.ON,FAIL_MSG)
            print(OK_MSG)

            #'''Global RUNNING'''
            #print(intro+"Global ON")
            #value =  epics.caget(nameGG)
            #print(space+nameGG+": "+self.sm_dic.setdefault(value,None))

            #self.assertEqual(value,self.ON,FAIL_MSG)
            #print(OK_MSG)


            '''ON --> OFF'''
            print(intro+"ON --> OFF")
            epics.caput(nameS,self.OFF,wait= False,timeout=5)
            value = waitUntilPV(nameG, self.OFF)

            print(space+nameG+": "+self.sm_dic.setdefault(value,None))
            
            self.assertEqual(value,self.OFF,FAIL_MSG)
            print(OK_MSG)

            #'''Global ON'''
            #print(intro+"Global ON")
            #value =  epics.caget(nameGG)
            #print(space+nameGG+": "+self.sm_dic.setdefault(value,None))

            #self.assertEqual(value,self.OFF,FAIL_MSG)
            #print(OK_MSG) 

            printv(self.line+
                   "\n| REQUIREMENTS\n"+
                   "| NDS-SRS-I-0120\n"+
                   "| NDS-SRS-I-0130\n"+
                   "| NDS-SRS-F-1140\n"+
                   "| NDS-SRS-F-1150\n"+
                   self.line,1)



            
            

        except KeyboardInterrupt:
            print("KeyboardInterrupt")
            self.ioc.stop()
            ioc = None
            print("Asserting False-Test interrupted manually")
            self.assertEqual(1,0)

    
       
        
       
if __name__ == '__main__':
    unittest.main()
