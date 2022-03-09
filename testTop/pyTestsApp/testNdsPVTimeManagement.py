#!/usr/bin/env python
import unittest
import epics
from epics import ca
import subprocess
from time import sleep
import iocControl
from iocControl import printv
import ioctests
from parametrizedTestCase import ParametrizedTestCase
from testUtils import waitUntilPV

def handle_messages(text):
    pass



class TestNdsPVTimeManagement(ParametrizedTestCase):
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
            libFile = 'libnds3-DeviceTimestamping.so' 
            subsFile = 'Timestamping.substitutions'
            DeviceName = "B-0"
            DriverName = "DeviceTimestamping"
            
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
            print("|                TEST Timestamping provided by NDS Device Driver using FTE node")
            print("|")
            print(self.line)    
            print("|")
            printv("| Test timestamping provided by NDS Device Driver",1)
            if(self.param == "INIT=YES"):
                printv("| Initialization no RBV",1)       
            printv("|\n"+self.line,1)

            CBS1 = 'TEST'
            CBS2 = 'FCT0'
            BOARDTYPE = 'B'
            BOARDTYPEIDX='0'
            NAME = 'Timestamping'
            # if(self.param == "INIT=YES"):
            #     BOARDTYPEIDX='1'

            self.prefix = CBS1+'-'+CBS2\
                +'-HWCF:'+BOARDTYPE+'-'+BOARDTYPEIDX+'-'+NAME    
           
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
        NDS_EPOCH = 1514764800
        '''TODO NDS_EPOCS_TAI automatization '''
        NDS_EPOCH_TAI = NDS_EPOCH-37 
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
            
            enablePV = self.prefix+'-Enable'
            enablePV_RBV = self.prefix+'-Enable_RBV'
            
            nameG = self.prefix+'-StateMachine-getState'
            nameS = self.prefix + '-StateMachine-setState'
            nameGG = self.prefix + '-StateMachine-getGlobalState'
            
            '''Default State'''
            print("|---Default State")
            
            value =  waitUntilPV(nameG,self.OFF)
            print(space+nameG+": "+self.sm_dic.setdefault(value,None))
            
            self.assertEqual(value,self.OFF,FAIL_MSG)
            print(OK_MSG)
            
            '''Switching on device: OFF --> ON'''
            print(intro+"State Machine: OFF --> ON")
            epics.caput(nameS,self.ON,wait= False,timeout=5)
            sleep(2)
            
            value =  waitUntilPV(nameG,self.ON)
            print(space+nameG+": "+self.sm_dic.setdefault(value,None))
            
            self.assertEqual(value,self.ON,FAIL_MSG)
            print(OK_MSG)

            '''Starting device: ON --> RUNNING'''
            print(intro+"State Machine: ON --> RUNNING")
            epics.caput(nameS,self.RUNNING,wait= False,timeout=5)
            sleep(1)
            
            value =  waitUntilPV(nameG,self.RUNNING)
            print(space+nameG+": "+self.sm_dic.setdefault(value,None))
            
            self.assertEqual(value,self.RUNNING,FAIL_MSG)
            print(OK_MSG)
                       
            ''' By default EPICS Data PV record has its TSE field equals to 0 '''
            ''' We retrieve the system time in the timestamp field by default'''
            epics.caput(enablePV,0,wait= False,timeout=5)
            epics.caget(enablePV_RBV)
            print enablePV_RBV + ' timestamp TSE==0: ' +epics.pv.fmt_time(epics.pv.get_pv(enablePV_RBV).timestamp)
            
            ''' We set the TSE field to -2 in the Data PV'''
            epics.caput(enablePV_RBV + ".TSE",-2,wait=True,timeout=5)
            
            sleep(1)
            epics.caput(enablePV,1,wait= False,timeout=5)
            
            '''Now, we retrieve the timestamp provided by the NDS Device Driver. For testing purposes this timestamp is always 2018-01-01 01:00:01.51476'''
            epics.caget(enablePV_RBV)
            value = epics.pv.get_pv(enablePV_RBV).timestamp
            '''TAI to UTC leap seconds = 37 for the NDS_EPOCH date. Source: https://www.ietf.org/timezones/data/leap-seconds.list '''
            #self.assertEqual(value,NDS_EPOCH_TAI) 
            value =epics.pv.fmt_time(epics.pv.get_pv(enablePV_RBV).timestamp)
            print enablePV_RBV+' timestamp TSE==-2: ' + value
            sleep(1)
            
            '''RUNNING --> ON'''
            print("\n")
            print(intro+"State Machine: RUNNING --> ON")
            epics.caput(nameS,self.ON,wait= True,timeout=5)
            sleep(2)
            
            value =  waitUntilPV(nameG,self.ON)
            print(space+nameG+": "+self.sm_dic.setdefault(value,None))
            
            self.assertEqual(value,self.ON,FAIL_MSG)
            print(OK_MSG)

            '''ON --> OFF'''
            print("\n")
            print(intro+"State Machine: ON --> OFF")
            epics.caput(nameS,self.OFF,wait= False,timeout=5)
            sleep(1)
            
            value =  waitUntilPV(nameG,self.OFF)
            print(space+nameG+": "+self.sm_dic.setdefault(value,None))
            
            self.assertEqual(value,self.OFF,FAIL_MSG)
            print(OK_MSG)

            '''
            printv(self.line+
                   "\n| REQUIREMENTS\n"+
                   "| NDS-SRS-I-0120\n"+
                   "| NDS-SRS-I-0130\n"+
                   "| NDS-SRS-F-1140\n"+
                   "| NDS-SRS-F-1150\n"+
                   self.line,1)
            '''
        except KeyboardInterrupt:
            print("KeyboardInterrupt")
            self.ioc.stop()
            ioc = None
            print("Asserting False-Test interrupted manually")
            self.assertEqual(1,0)

    
       
        
       
if __name__ == '__main__':
    unittest.main()
