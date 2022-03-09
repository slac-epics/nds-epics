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



class TestNdsTiming(ParametrizedTestCase):
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
    
    NOT_SYNCED = 0
    SYNCING = 1
    SYNCED = 2
    LOST_SYNC = 3

    line = "+---------------------------------------------------------------------"
    
    sm_dic = {UNKNOWN:'UNKNOWN',OFF:'OFF',SWITCH_OFF:'SWITCH_OFF',INITIALIZING:'INITIALIZING',ON:'ON',STOPPING:'STOPPING',STARTING:'STARTING',RUNNING:'RUNNING', FAULT:'FAULT',None:'NONE'}
    tm_dic ={NOT_SYNCED:"NOT_SYNCED",SYNCING:"SYNCING",SYNCED:"SYNCED", LOST_SYNC:" LOST_SYNC"}

    def setUp(self):
        try:
            ioctests.setup()
            ca.initialize_libca()
            #epics.ca.replace_printf_handler(handle_messages)
            self.ioc = iocControl.iocControl()
            self.ioc.startIOC() 
            
            appName = 'ndsex1'
            libFile = 'libnds3-DeviceTiming.so' 
            subsFile = 'Timing.substitutions'
            DeviceName = "B-0"
            DriverName = "DeviceTiming"
            # if(self.param == "INIT=YES"):
            #      DeviceName = "B-1"
            #      subsFile = 'Timing2.substitutions'
            iocCmd =  self.ioc.iocCommandCompose(appName, libFile,subsFile,DeviceName,DriverName,self.param)
            
           
            #print("")
            #print(iocCmd) 
            
            self.ioc.iocProcess.stdin.write(iocCmd)
            sleep(2)
            print(self.line)
            print("|")
            print("|                    TEST NDS TIMING NODE")
            print("|")
            print(self.line)    
            print("|")
            if(self.param == "INIT=YES"):
                printv("| Initialization no RBV",1)
            printv("| Check the initialization PV values:\n"+
                   "|  - ClkFrequency\n"+
                   "|  - ClkMultiplier\n"+
                   "|  - SyncStatus\n"+
                   "|  - SecsLastSync\n"+
                   "|  - RefTimeBase\n"+
                   "| Start de Timming and read the time pushed from the Timming thread to EPICS\n"+
                   "| Check the transitions of state machine\n"+
                   "| Check the SyncStatus and SecsLastSync PVs \n"+
                   "|\n"+
                   self.line,1)
            CBS1 = 'TEST'
            CBS2 = 'FCT0'
            BOARDTYPE = 'B'
            BOARDTYPEIDX='0'
            Timing_NAME = 'Timing'
            # if(self.param == "INIT=YES"):
            #     BOARDTYPEIDX='1'

            self.prefix = CBS1+'-'+CBS2\
                +'-HWCF:'+BOARDTYPE+'-'+BOARDTYPEIDX+'-'+Timing_NAME 
           
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
        NDS_EPOCH = 1514764800  # NDS_EPOCH is equals to 01/01/2018 in UTC format 
        
        epics.ca.replace_printf_handler(handle_messages)
        #space = "    "
        intro = "|---"
        space = "|   "
        try:   
            nameG = self.prefix+'-StateMachine-getState'
            nameS = self.prefix + '-StateMachine-setState'
            nameGG = self.prefix + '-StateMachine-getGlobalState'
            
            '''Default State'''
            print("|---Default State")
            
            value =  waitUntilPV(nameG,self.OFF)
            print(space+nameG+": "+self.sm_dic.setdefault(value,None))
            
            self.assertEqual(value,self.OFF,FAIL_MSG)
            print(OK_MSG)
            
            

            # ''' Default Global '''
            # print(intro+"Default Global State")
            # value =  epics.caget(nameGG)
            # print(space+nameGG+": "+self.sm_dic.setdefault(value,None))

            # self.assertEqual(value,self.OFF,FAIL_MSG)
            # print(OK_MSG)


            '''Syncronization Status in OFF'''
            print(intro+"Syncronization Status in OFF")
            nameG = self.prefix+"-SyncStatus"
            
            value =  waitUntilPV(nameG,self.NOT_SYNCED)
            
            print(space+nameG+": "+self.tm_dic.setdefault(value,None))
            
            self.assertEqual(value,self.NOT_SYNCED,FAIL_MSG)
            print(OK_MSG)

            '''OFF --> ON'''
            nameG = self.prefix+'-StateMachine-getState'
            nameS = self.prefix + '-StateMachine-setState'
            nameGG = self.prefix + '-StateMachine-getGlobalState'

            print(intro+"OFF --> ON")
            epics.caput(nameS,self.ON,wait= False,timeout=5)
            sleep(2)
            
            value =  waitUntilPV(nameG,self.ON)
            print(space+nameG+": "+self.sm_dic.setdefault(value,None))
            
            self.assertEqual(value,self.ON,FAIL_MSG)
            print(OK_MSG)
            
            
            # '''Global ON'''
            # print(intro+"Global ON")
            
            # value =  epics.caget(nameGG)
            # print(space+nameGG+": "+self.sm_dic.setdefault(value,None))

            # self.assertEqual(value,self.ON,FAIL_MSG)
            # print(OK_MSG)
           
           
            '''Syncronization Status in ON'''
            print(intro+"Syncronization Status in ON")
            nameG = self.prefix+"-SyncStatus"
            
            value =  waitUntilPV(nameG,self.SYNCING)
            
            print(space+nameG+": "+self.tm_dic[value])
            
            self.assertEqual(value,self.SYNCING,FAIL_MSG)
            print(OK_MSG)

            '''Clock Frequency'''
            print(intro+"Clock Frequency")
            nameG = self.prefix+"-ClkFrequency"
            
            value =  waitUntilPV(nameG,100.001)
            
            print(space+nameG+": "+str(value))

            self.assertEqual(value,100.001,FAIL_MSG)
            print(OK_MSG)
 
            '''Clock Multiplier'''
            print(intro+"Clock Multiplier")
            nameG = self.prefix+"-ClkMultiplier"
            
            value =  waitUntilPV(nameG,2)
            
            print(space+nameG+": "+str(value))
            
            self.assertEqual(value,2,FAIL_MSG)
            print(OK_MSG)

            '''SecLastSync'''
            print(intro+"Second from Last Syncronization")
            nameG =  self.prefix+"-SecsLastSync"
            
            value =  waitUntilPV(nameG,0)
            
            print(space+nameG+": "+str(value))
            
            self.assertEqual(value,0,FAIL_MSG)
            print(OK_MSG)


            '''Reference Time Base'''
            print(intro+"Reference Time Base")
            nameG =  self.prefix+"-RefTimeBase"
            
            value =  epics.caget(nameG)
            
            print(space+nameG+": "+str(value[0])+" sec and "+str(value[1])+" ns")
            
            self.assertEqual(value[0], NDS_EPOCH,FAIL_MSG)
            self.assertEqual(value[1], NDS_EPOCH+10,FAIL_MSG)
            print(OK_MSG)

            "SubArray Test Reference Time Base"
            nameG = self.prefix+"-RefTimeBaseSec"
            value =  waitUntilPV(nameG, NDS_EPOCH)
            print(space+nameG+": "+str(value)+" sec")
            self.assertEqual(value, NDS_EPOCH,FAIL_MSG)
            print(OK_MSG)

            nameG = self.prefix+"-RefTimeBaseNano"
            value =  waitUntilPV(nameG, NDS_EPOCH+10)
            print(space+nameG+": "+str(value)+" ns")
            self.assertEqual(value, NDS_EPOCH+10,FAIL_MSG)
            print(OK_MSG)

            
            '''ON --> RUNNING'''
            print(intro+"ON --> RUNNING")
            nameG = self.prefix+'-StateMachine-getState'
            nameS = self.prefix + '-StateMachine-setState'
            nameGG = self.prefix + '-StateMachine-getGlobalState'

            epics.caput(nameS,self.RUNNING,wait= False,timeout=5)
            sleep(1)

            value =  waitUntilPV(nameG,self.RUNNING)
            print(space+nameG+": "+self.sm_dic.setdefault(value,None))
            
            self.assertEqual(value,self.RUNNING,FAIL_MSG)
            print(OK_MSG)

            '''Syncronization Status'''
            print(intro+"Syncronization Status in Running")
            nameG = self.prefix+"-SyncStatus"
            
            value =  waitUntilPV(nameG,self.SYNCED)
            
            print(space+nameG+": "+self.tm_dic[value])
            
            self.assertEqual(value,self.SYNCED,FAIL_MSG)
            print(OK_MSG)

            # '''Global RUNNING'''
            # print(intro+"Global RUNNING")
            # value =  epics.caget(nameGG)
            # print(space+nameGG+": "+self.sm_dic.setdefault(value,None))

            # self.assertEqual(value,self.RUNNING,FAIL_MSG)
            # print(OK_MSG)
           

            '''Time'''
            print(intro+"Time")
            nameG = self.prefix+"-Time"
            
            value =  epics.caget(nameG)
        
            print(space+nameG+": "+str(value[0])+" sec and "+str(value[1])+" ns")
            
            # These values are hard-coded in the timing nds device driver
            self.assertEqual(value[0], NDS_EPOCH,FAIL_MSG)
            self.assertEqual(value[1], 20091982,FAIL_MSG) 
            print(OK_MSG)

            "SubArray Test Time"
            nameG = self.prefix+"-TimeSec"
            value =  epics.caget(nameG)
            print(space+nameG+": "+str(value)+" sec")
            self.assertEqual(value, NDS_EPOCH,FAIL_MSG)
            print(OK_MSG)

            nameG = self.prefix+"-TimeNano"
            value =  epics.caget(nameG)
            print(space+nameG+": "+str(value)+" ns")
            self.assertEqual(value, 20091982,FAIL_MSG)
            print(OK_MSG)
           


            '''HTIME'''
            print(intro+"HTime")
            nameG = self.prefix+"-HTime"
            
            value =  epics.caget(nameG,as_string=True)
            
            print(space+nameG+": "+value)
            
            self.assertEqual(value,"Mon Jan  1 00:00:00 2018",FAIL_MSG)
            print(OK_MSG)



            '''RUNNING --> ON'''
            print(intro+"RUNNING --> ON")

            nameG = self.prefix+'-StateMachine-getState'
            nameS = self.prefix + '-StateMachine-setState'
            nameGG = self.prefix + '-StateMachine-getGlobalState'

            epics.caput(nameS,self.ON,wait= False,timeout=5)
            sleep(1)
            
            value =  epics.caget(nameG)
            print(space+nameG+": "+self.sm_dic.setdefault(value,None))
            
            self.assertEqual(value,self.ON,FAIL_MSG)
            print(OK_MSG)

            # '''Global RUNNING'''
            # print(intro+"Global ON")
            # value =  epics.caget(nameGG)
            # print(space+nameGG+": "+self.sm_dic.setdefault(value,None))

            # self.assertEqual(value,self.ON,FAIL_MSG)
            # print(OK_MSG)

            

            '''ON --> OFF'''
            print(intro+"ON --> OFF")
            nameG = self.prefix+'-StateMachine-getState'
            nameS = self.prefix + '-StateMachine-setState'
            nameGG = self.prefix + '-StateMachine-getGlobalState'
            epics.caput(nameS,self.OFF,wait= False,timeout=5)
            sleep(1)
            
            value =  epics.caget(nameG)
            print(space+nameG+": "+self.sm_dic.setdefault(value,None))
            
            self.assertEqual(value,self.OFF,FAIL_MSG)
            print(OK_MSG)

            
            # '''Global OFF'''
            # print(intro+"Global OFF")
            # value =  epics.caget(nameGG)
            # print(space+nameGG+": "+self.sm_dic.setdefault(value,None))

            # self.assertEqual(value,self.OFF,FAIL_MSG)
            # print(OK_MSG) 

            
            '''Syncronization Status in OFF'''
            print(intro+"Syncronization Status in OFF")
            nameG = self.prefix+"-SyncStatus"
            
            value =  epics.caget(nameG)
            
            print(space+nameG+": "+self.tm_dic[value])
            
            self.assertEqual(value,self.NOT_SYNCED,FAIL_MSG)
            print(OK_MSG)


            '''SecLastSync OFF'''
            print(intro+"Second from Last Syncronization Switching OFF (Hard Coded)")
            nameG =  self.prefix+"-SecsLastSync"
            
            value =  epics.caget(nameG)
            
            print(space+nameG+": "+str(value))
            
            self.assertEqual(value,10,FAIL_MSG)
            print(OK_MSG)
            
            printv(self.line+
                   "\n| REQUIREMENTS\n"+
                   "| NDS-SRS-I-0120\n"+
                   "| NDS-SRS-I-0130\n"+
                   "| NDS-SRS-F-1140\n"+
                   "| NDS-SRS-F-1150\n"+
                   "| NDS-SRS-F-0620\n"+
                   "| NDS-SRS-F-1370\n"+
                   self.line,1)

        except KeyboardInterrupt:
            print("KeyboardInterrupt")
            self.ioc.stop()
            ioc = None
            print("Asserting False-Test interrupted manually")
            self.assertEqual(1,0)

    
       
        
       
if __name__ == '__main__':
    unittest.main()
