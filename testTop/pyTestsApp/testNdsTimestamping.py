#!/usr/bin/env python
import unittest
import epics
from epics import ca
import subprocess
from time import sleep,ctime
import iocControl
from iocControl import printv
import ioctests
from parametrizedTestCase import ParametrizedTestCase
from testUtils import waitUntilPV

def handle_messages(text):
    pass



class TestNdsTimestamping(ParametrizedTestCase):
    '''Testing basic load and initialization of NDS driver in EPICS'''
    ''' 1-setup
    2-test***
    3-tearDown
    '''
    
    prefix =""
    ioc= None
    
    
    #State machine
    UNKNOWN = 0
    OFF = 1
    SWITCH_OFF = 2
    INITIALIZING = 3
    ON = 4
    STOPPING = 5
    STARTING = 6
    RUNNING = 7
    FAULT = 8
    
    #Enable/Disable
    EN_OFF = 0
    EN_ON = 1

    #Edge
    RISING = 0
    FALLING = 1
    ANY_EDGE = 2
    
    #Overflow
    
    NO_OVERFLOW = 0
    OVERFLOWED = 1
    FULL_OVERFLOW = 2
    ERROR_OVERFLOW = 3

    #Clear Overflow
    CLEAR_NO = 0
    CLEAR_YES = 1

    line = "+---------------------------------------------------------------------"

    sm_dic = {UNKNOWN:'UNKNOWN',OFF:'OFF',SWITCH_OFF:'SWITCH_OFF',INITIALIZING:'INITIALIZING',ON:'ON',STOPPING:'STOPPING',STARTING:'STARTING',RUNNING:'RUNNING', FAULT:'FAULT',None:'NONE'}
    
    enable_dic = {EN_OFF:"OFF",EN_ON:"ON",None:"None"}
    
    edge_dic = {RISING:"RISING",FALLING:"FALLING",ANY_EDGE:"ANY",None:"None"}
    
    overflow_dic = {NO_OVERFLOW:"NO",OVERFLOWED:"OVERFLOWED",FULL_OVERFLOW:"FULL",ERROR_OVERFLOW:"ERROR",None:"None"}
    
    clear_dic = {CLEAR_YES:"CLEAR YES",CLEAR_NO:"CLEAR NO"}

    
    def setUp(self):
        try:
            ioctests.setup()
            ca.initialize_libca()
            epics.ca.replace_printf_handler(handle_messages)
            self.ioc = iocControl.iocControl()
            self.ioc.startIOC() 
            
            appName = 'ndsex1'
            libFile = 'libnds3-DeviceTimestamping.so' 
            subsFile = 'Timestamping.substitutions'
            DeviceName = "B-0"
            DriverName = "DeviceTimestamping"
            # if(self.param == "INIT=YES"):
            #      DeviceName = "B-1"
            #      subsFile = 'Timestamping2.substitutions'

            iocCmd =  self.ioc.iocCommandCompose(appName, libFile,subsFile,DeviceName,DriverName,self.param)
            #print("")
            #print(iocCmd) 
            
            self.ioc.iocProcess.stdin.write(iocCmd)
            sleep(2)
            print(self.line)
            print("|")
            print("|                    TEST TIMESTAMPING NODE")
            print("|")
            print(self.line)    
            print("|")
            printv("| Check the initialization PV values:",1)
            if(self.param == "INIT=YES"):
                printv("|  - Enable \n"+
                       "|  - Edge\n"+
                       "|  - ClearOverflow",1)
            printv("|  - Enable_RBV\n"+
                   "|  - Edge_RBV\n"+
                   "|  - MaxTimestamps\n"+
                   "|  - Overflow\n"+
                   "| Start the Timestamping and acquires all timestamp pushed to EPICS\n"+
                   "| Check that the acquired data are correct\n"+
                   "| Check the transitions of state machine\n"+
                   "|\n"+
                   self.line,1)

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
        #sleep(11)
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
        timestamps=[]
        timestamps_and_overflow = []
        
        def onChanges(pvname=None, value=None, **kw):
            timestamps.append([value,ctime()])
            timestamps_and_overflow.append(["T",value])
            
        def onChangesOver(pvname=None, value=None, **kw):
            timestamps_and_overflow.append(["O",value])

            
        try:
            
            
            if(self.param == "INIT=YES"):
                '''Testing Initialization'''
                print("|---Default Initialization no RBV")

                nameS = self.prefix+"-Enable"
                '''Enable'''
                value =  waitUntilPV(nameS,self.EN_ON)
                print(space+nameS+": "+self.enable_dic.setdefault(value,None))
                self.assertEqual(value,self.EN_ON,FAIL_MSG)
                 
                nameS = self.prefix + '-Edge'
                value =  waitUntilPV(nameS,self.FALLING)
                print(space+nameS+": "+self.edge_dic.setdefault(value,None))
                self.assertEqual(value,self.FALLING,FAIL_MSG)

                nameS = self.prefix + '-ClearOverflow'
                value =  waitUntilPV(nameS,self.CLEAR_YES)
                print(space+nameS+": "+self.clear_dic.setdefault(value,None))
                self.assertEqual(value,self.CLEAR_YES,FAIL_MSG)
                
                
                print(OK_MSG)
 
            # nameG = self.prefix+"-StateMachine-setState"
            # '''Enable'''
            # print("|---Default ****")
            # value =  epics.caget(nameG)
            # print(space+nameG+": "+str(value))
            
            # #self.assertEqual(value,self.EN_ON,FAIL_MSG)
            #     #print(nameG+" "+str(value))
            #     #print("Sleeping")
            #     #sleep(15)
                
            # print(OK_MSG)

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
            
            
            # # '''Global ON'''
            # # print(intro+"Global ON")
            
            # # value =  epics.caget(nameGG)
            # # print(space+nameGG+": "+self.sm_dic.setdefault(value,None))

            # # self.assertEqual(value,self.ON,FAIL_MSG)
            # # print(OK_MSG)
           
           
            '''Enable Status'''
            print(intro+"Enabled in ON")
            nameG = self.prefix+"-Enable_RBV"
            
            value =  waitUntilPV(nameG,self.EN_OFF)
            
            print(space+nameG+": "+self.enable_dic[value])
            
            self.assertEqual(value,self.EN_OFF,FAIL_MSG)
            print(OK_MSG)



            '''Edge Status'''
            print(intro+"Edge")
            nameG = self.prefix+"-Edge_RBV"
            
            value =  waitUntilPV(nameG,self.FALLING)
            
            print(space+nameG+": "+self.edge_dic.setdefault(value,None))
            
            self.assertEqual(value,self.FALLING,FAIL_MSG)
            print(OK_MSG) 


            '''Max Number Timestamps'''
            print(intro+"Maximum number Timestamps")
            nameG = self.prefix+"-MaxTimestamps"
            
            value =  waitUntilPV(nameG,5)
            
            print(space+nameG+": "+str(value))
            
            self.assertEqual(value,5,FAIL_MSG)
            print(OK_MSG) 


            '''Overflow Status'''
            print(intro+"Overflow status")
            nameG = self.prefix+"-Overflow"
            
            value =  waitUntilPV(nameG,self.NO_OVERFLOW)
            
            print(space+nameG+": "+self.overflow_dic[value])
            
            self.assertEqual(value,self.NO_OVERFLOW,FAIL_MSG)
            print(OK_MSG) 
           
            '''Timestamp Callback'''
            
            pvname = self.prefix+"-Overflow"
            pv_timestamps = epics.PV(pvname)
            pv_timestamps.add_callback(onChangesOver)

            pvname = self.prefix+"-Timestamps"
            pv_timestamps = epics.PV(pvname)
            pv_timestamps.add_callback(onChanges)
            
           
            
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


            # '''Global RUNNING'''
            # print(intro+"Global RUNNING")
            # value =  epics.caget(nameGG)
            # print(space+nameGG+": "+self.sm_dic.setdefault(value,None))

            # self.assertEqual(value,self.RUNNING,FAIL_MSG)
            # print(OK_MSG)
            
            '''Change Edge'''
            print(intro+"Change Edge to ANY")
            nameG = self.prefix+'-Edge_RBV'
            nameS = self.prefix + '-Edge'
           
            epics.caput(nameS,self.ANY_EDGE,wait= False,timeout=5)
            sleep(1)

            value =  waitUntilPV(nameG,self.ANY_EDGE)
            print(space+nameG+": "+self.edge_dic[value])
            
            self.assertEqual(value,self.ANY_EDGE,FAIL_MSG)
            print(OK_MSG)

            

            '''Change Enable to ON'''
            print(intro+"Change Enable to ON")
            nameG = self.prefix+'-Enable_RBV'
            nameS = self.prefix + '-Enable'
           
            epics.caput(nameS,self.EN_ON,wait= False,timeout=5)
            sleep(2)

            value =  waitUntilPV(nameG,self.EN_ON)
            print(space+nameG+": "+self.enable_dic[value])
            
            self.assertEqual(value,self.EN_ON,FAIL_MSG)
            print(OK_MSG)


            
            '''Timestamp'''
            print(intro+"Timestamp")
            nameG = self.prefix+"-Timestamps"
            print(space+"Waiting for the buffer")
            
            
            expected_sec = [0,0,0,0,0,0]
            expected_nsec = [0,10,10,10,10,10]
            #expected_edge = [0,0,0,1,1,0]
            expected_edge = [1,1,1,0,0,1]
            expected_id = [1,2,3,4,5,6]
            
            sleep(10)
            
            k=0
            for timestamp in timestamps[1:]:
                ts = timestamp[0]
                print(space+"Timestamps:"+str(ts))
                sec = ts[0]
                nsec = ts[1]
                Id = ts[2] 
                edge = ts[3]

                self.assertEqual(sec,expected_sec[k],FAIL_MSG)
                #self.assertEqual(nsec,expected_nsec[k],FAIL_MSG)#TODO Test according to TAI UTC changes.
                self.assertEqual(edge,expected_edge[k],FAIL_MSG)
                self.assertEqual(Id,expected_id[k],FAIL_MSG)
                k = k +1
                 
            print(OK_MSG) 
            
            "Testing Subarray Timestamps"
            print(intro+"TimestampSec")
            nameG = self.prefix+"-TimestampsSec"
            value =  waitUntilPV(nameG,expected_sec[5])
            print(space+nameG+": "+str(value)+" sec")
            
            self.assertEqual(value,expected_sec[5],FAIL_MSG)
            print(OK_MSG)

            print(intro+"TimestampsNano")
            nameG = self.prefix+"-TimestampsNano"
            value =  epics.caget(nameG)
            print(space+nameG+": "+str(value)+" ns")
            
            #self.assertEqual(value,expected_nsec[5],FAIL_MSG)#TODO Test according to TAI UTC changes.
            #print(OK_MSG)#TODO Test according to TAI UTC changes.

            print(intro+"TimestampID")
            nameG = self.prefix+"-TimestampsID"
            value =  waitUntilPV(nameG,expected_id[5])
            print(space+nameG+": "+str(value))
            
            self.assertEqual(value,expected_id[5],FAIL_MSG)
            print(OK_MSG)

            print(intro+"TimestampsIsRising")
            nameG = self.prefix+"-TimestampsIsRising"
            value =  waitUntilPV(nameG,expected_edge[5])
            print(space+nameG+": "+str(value))
            
            self.assertEqual(value,expected_edge[5],FAIL_MSG)
            print(OK_MSG)


            '''Overflow Status All'''
            print(intro+"Overflow status All")
            k = 0
            kold = -1
            over = []
            over_tmp = 0
            
            for item in timestamps_and_overflow: 
               
                if(item[0]=='O'):
                    over_tmp = item[1]
                
                if(kold!=k):    
                    over.append(over_tmp)
                    kold = k
                

                if(item[0]=='T' and len(item[1])>0):
                    k = k+1

        
            for k in range(6):
                value = over[k]
                print("Number of timestamps stored:"+str(k+1) \
                          +" OVERFLOW: "+self.overflow_dic[value])
                if(k<4):
                    self.assertEqual(value,self.NO_OVERFLOW,FAIL_MSG)
                if(k==4):
                    self.assertEqual(value,self.FULL_OVERFLOW,FAIL_MSG)
                if(k==5):
                    self.assertEqual(value,self.OVERFLOWED,FAIL_MSG)

            print(OK_MSG) 
                    


            '''Clear Overflow'''
            print(intro+"Clear Overflow")
            
            nameS = self.prefix + '-ClearOverflow'
           
            epics.caput(nameS,42,wait= False,timeout=5)
            sleep(2)
            nameG = self.prefix+"-Overflow"
        
            value =  waitUntilPV(nameG,self.NO_OVERFLOW)
            
            print(space+nameG+": "+self.overflow_dic[value])
            
            self.assertEqual(value,self.NO_OVERFLOW,FAIL_MSG)
            print(OK_MSG) 
           



            '''RUNNING --> ON'''
            print(intro+"RUNNING --> ON")

            nameG = self.prefix+'-StateMachine-getState'
            nameS = self.prefix + '-StateMachine-setState'
            nameGG = self.prefix + '-StateMachine-getGlobalState'

            epics.caput(nameS,self.ON,wait= False,timeout=5)
            sleep(1)
            
            value =  waitUntilPV(nameG,self.ON)
            print(space+nameG+": "+self.sm_dic.setdefault(value,None))
            
            self.assertEqual(value,self.ON,FAIL_MSG)
            print(OK_MSG)


            

            '''ON --> OFF'''
            print(intro+"ON --> OFF")
            nameG = self.prefix+'-StateMachine-getState'
            nameS = self.prefix + '-StateMachine-setState'
            nameGG = self.prefix + '-StateMachine-getGlobalState'
            epics.caput(nameS,self.OFF,wait= False,timeout=5)
            sleep(1)
            
            value =  waitUntilPV(nameG,self.OFF)
            print(space+nameG+": "+self.sm_dic.setdefault(value,None))
            
            self.assertEqual(value,self.OFF,FAIL_MSG)
            print(OK_MSG)

            
            # '''Global OFF'''
            # print(intro+"Global OFF")
            # value =  epics.caget(nameGG)
            # print(space+nameGG+": "+self.sm_dic.setdefault(value,None))

            # self.assertEqual(value,self.OFF,FAIL_MSG)
            # print(OK_MSG) 

            printv(self.line+
                   "\n| REQUIREMENTS\n"+
                   "| NDS-SRS-I-0120\n"+
                   "| NDS-SRS-I-0130\n"+
                   "| NDS-SRS-F-1140\n"+
                   "| NDS-SRS-F-1150\n"+
                   "| NDS-SRS-F-0700\n"+
                   "| NDS-SRS-F-0710\n"+
                   "| NDS-SRS-F-0720\n"+
                   "| NDS-SRS-F-1460\n"+
                   "| NDS-SRS-F-1480\n"+
                   "| NDS-SRS-F-1490\n"+
                   self.line,1)
            
        except KeyboardInterrupt:
            print("KeyboardInterrupt")
            self.ioc.stop()
            ioc = None
            print("Asserting False-Test interrupted manually")
            self.assertEqual(1,0)

    
       
        
       
if __name__ == '__main__':
    unittest.main()
