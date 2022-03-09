#!/usr/bin/env python
import unittest
import epics
from epics import ca
import subprocess
from time import sleep
import iocControl
from iocControl import printv
import ioctests
from testUtils import waitUntilPV
from parametrizedTestCase import ParametrizedTestCase

def handle_messages(text):
    pass



class TestNdsHQMonitor(ParametrizedTestCase):
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
            libFile = 'libnds3-DeviceHQMonitor.so' 
            subsFile = 'HQMonitor.substitutions'
            DeviceName = "B-0"
            DriverName = "DeviceHQMonitor"

            iocCmd =  self.ioc.iocCommandCompose(appName, libFile,subsFile,DeviceName,DriverName,self.param)
            #print("")
            #print(iocCmd) 
            
            self.ioc.iocProcess.stdin.write(iocCmd)
            sleep(2)
            print(self.line)
            print("|")
            print("|                    TEST HQ MONITOR NODE")
            print("|")
            print(self.line)    
            print("|")
            
            if(self.param == "INIT=YES"):
                printv("| Check the initialization PV values:",1)
                printv("|  - SEUEnable (initial value)" ,1)
            printv("| HQMonitor node status:\n"+
                   "|  - DevPower\n"+
                   "|  - DevTemperature\n"+
                   "|  - DevVoltage\n"+
                   "|  - DevCurrent\n"+
                   "| Set and check the PV values to configure the HQMonitor Node:\n"+
                   "|  - SEUEnable\n"+
                   "|  - DAQEnable\n"+
                   "|  - TestTxtResult\n"+
                   "|  - TestEnable\n"+
                   "|  - TestType\n"+
                   "|  - TestVerboseEnable\n"+
                   "|  - TestIDEnable\n"+
                   "|  - TestTxtEnable\n"+
                   "|  - TestCodeResults\n"+
                   "|  - TestTxtResults\n"+
                   "|  - SignalQFlag\n"+
                   "|  - SignalQFlagTrigLevel\n"+
                   "| Check the transitions of state machine.\n"+
                   "|\n"+
                   self.line,1)
            CBS1 = 'TEST'
            CBS2 = 'FCT0'
            BOARDTYPE = 'B'
            BOARDTYPEIDX='0'
            HQMonitor_NAME = 'HQMonitor'
            

            self.prefix = CBS1+'-'+CBS2\
                +'-HWCF:'+BOARDTYPE+'-'+BOARDTYPEIDX+'-'+HQMonitor_NAME 
           
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
        try:  
            if(self.param == "INIT=YES"):
                '''Testing Initialization'''
                print("|---Default Initialization no RBV")
                nameS = self.prefix+"-SEUEnable"
                
                value =  waitUntilPV(nameS,101)
                
                print(space+nameS+": "+str(value))
                self.assertEqual(value,101,FAIL_MSG)
                print(OK_MSG)
            
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


            '''ON --> RUNNING'''
            print(intro+"ON --> RUNNING")
            epics.caput(nameS,self.RUNNING,wait= False,timeout=5)
            sleep(1)

            value = waitUntilPV(nameG,self.RUNNING)
            print(space+nameG+": "+self.sm_dic.setdefault(value,None))
            
            self.assertEqual(value,self.RUNNING,FAIL_MSG)
            print(OK_MSG)

            

            # '''Global RUNNING'''
            # print(intro+"Global RUNNING")
            # value =  epics.caget(nameGG)
            # print(space+nameGG+": "+self.sm_dic.setdefault(value,None))

            # self.assertEqual(value,self.RUNNING,FAIL_MSG)
            # print(OK_MSG)


            '''Device Power'''
            print(intro+"Device Power")
            nameG = self.prefix+"-DevPower"
            
            value =  waitUntilPV(nameG,0.25)
            
            print(space+nameG+": "+str(value))
            
            self.assertEqual(value,0.25,FAIL_MSG)
            print(OK_MSG)


            '''Device Temperatur'''
            print(intro+"Device Temperature")
            nameG = self.prefix+"-DevTemperature"
            
            value =  waitUntilPV(nameG,295.5)
            
            print(space+nameG+": "+str(value))
            
            self.assertEqual(value,295.5,FAIL_MSG)
            print(OK_MSG)


            '''Device Voltage'''
            print(intro+"Device Voltage")
            nameG = self.prefix+"-DevVoltage"
            
            value =  waitUntilPV(nameG,2.5)
            
            print(space+nameG+": "+str(value))
            
            self.assertEqual(value,2.5,FAIL_MSG)
            print(OK_MSG)

            '''Device Current'''
            print(intro+"Device Current")
            nameG = self.prefix+"-DevCurrent"
            
            value =  waitUntilPV(nameG,0.1)
            
            print(space+nameG+": "+str(value))
            
            self.assertEqual(value,0.1,FAIL_MSG)
            print(OK_MSG)


            '''SEU Enable'''
            print(intro+"Enable Detection Single Events Upsets")
            nameG = self.prefix+"-SEUEnable_RBV"
            nameS = self.prefix+"-SEUEnable"
            
            value =  waitUntilPV(nameG,0)
            
            print(space+nameG+": "+str(value))
            
            self.assertEqual(value,0,FAIL_MSG)
            print(OK_MSG)


            '''Change SEU Enable'''
            print(intro+"Change Enable Detection SEU")

            epics.caput(nameS,1,wait= False,timeout=5)
            sleep(2)

            value =  waitUntilPV(nameG,1)
            print(space+nameG+": "+str(value))
            
            self.assertEqual(value,1,FAIL_MSG)
            print(OK_MSG)


            '''DAQ Enable'''
            print(intro+"DAQ Enable")
            nameG = self.prefix+"-DAQEnable_RBV"
            nameS = self.prefix+"-DAQEnable"
            
            value =  waitUntilPV(nameG,0)
            
            print(space+nameG+": "+str(value))
            
            self.assertEqual(value,0,FAIL_MSG)
            print(OK_MSG)


            '''Change DAQ Enable'''
            print(intro+"Change DAQ Enable")

            epics.caput(nameS,1,wait= False,timeout=5)
            sleep(2)

            value =  waitUntilPV(nameG,1)
            print(space+nameG+": "+str(value))
             
            self.assertEqual(value,1,FAIL_MSG)
            print(OK_MSG)
            


            '''self Test Txt Results'''
            print(intro+"self Test Txt Reuslts")
            nameG = self.prefix+"-TestTxtResult"
            
            value =  epics.caget(nameG,as_string=True)
            
            print(space+nameG+": "+value)
            
            self.assertEqual(value,"",FAIL_MSG)
            print(OK_MSG)

            
            '''Test Enable'''
            print(intro+"Test Enable")
            nameG = self.prefix+"-TestEnable_RBV"
            nameS = self.prefix+"-TestEnable"
            
            value =  waitUntilPV(nameG,0)
            
            print(space+nameG+": "+str(value))
            
            self.assertEqual(value,0,FAIL_MSG)
            print(OK_MSG)


            '''Change Test Enable'''
            print(intro+"Change Test Enable")

            epics.caput(nameS,1,wait= False,timeout=5)
            sleep(2)

            value =  waitUntilPV(nameG,1)
            print(space+nameG+": "+str(value))
             
            self.assertEqual(value,1,FAIL_MSG)
            print(OK_MSG)

            '''Test Type'''
            print(intro+"Test Type")
            nameG = self.prefix+"-TestType_RBV"
            nameS = self.prefix+"-TestType"
            
            value =  waitUntilPV(nameG,0)
            
            print(space+nameG+": "+str(value))
            
            self.assertEqual(value,0,FAIL_MSG)
            print(OK_MSG)


            '''Change Test Type'''
            print(intro+"Change Test Type")

            epics.caput(nameS,1,wait= False,timeout=5)
            sleep(2)

            value =  waitUntilPV(nameG,1)
            print(space+nameG+": "+str(value))
             
            self.assertEqual(value,1,FAIL_MSG)
            print(OK_MSG)


            '''Test Verbose'''
            print(intro+"Test Verbose")
            nameG = self.prefix+"-TestVerboseEnable_RBV"
            nameS = self.prefix+"-TestVerboseEnable"
            
            value =  waitUntilPV(nameG,0)
            
            print(space+nameG+": "+str(value))
            
            self.assertEqual(value,0,FAIL_MSG)
            print(OK_MSG)


            '''Change Test Verbose'''
            print(intro+"Change Test Verbose")

            epics.caput(nameS,1,wait= False,timeout=5)
            sleep(2)

            value =  waitUntilPV(nameG,1)
            print(space+nameG+": "+str(value))
             
            self.assertEqual(value,1,FAIL_MSG)
            print(OK_MSG)


            '''ID Enable'''
            print(intro+"ID Enable")
            nameG = self.prefix+"-TestIDEnable_RBV"
            nameS = self.prefix+"-TestIDEnable"
            
            value =  waitUntilPV(nameG,0)
            
            print(space+nameG+": "+str(value))
            
            self.assertEqual(value,0,FAIL_MSG)
            print(OK_MSG)


            '''Change ID Enable'''
            print(intro+"Change Test ID Enable")

            epics.caput(nameS,1,wait= False,timeout=5)
            sleep(2)

            value =  waitUntilPV(nameG,1)
            print(space+nameG+": "+str(value))
             
            self.assertEqual(value,1,FAIL_MSG)
            print(OK_MSG)



            '''Test Txt Enable'''
            print(intro+"Txt Enable")
            nameG = self.prefix+"-TestTxtEnable_RBV"
            nameS = self.prefix+"-TestTxtEnable"
            
            value =  waitUntilPV(nameG,0)
            
            print(space+nameG+": "+str(value))
            
            self.assertEqual(value,0,FAIL_MSG)
            print(OK_MSG)


            '''Change Txt Enable'''
            print(intro+"Change Test Txt Enable")

            epics.caput(nameS,1,wait= False,timeout=5)
            sleep(2)

            value =  waitUntilPV(nameG,1)
            print(space+nameG+": "+str(value))
             
            self.assertEqual(value,1,FAIL_MSG)
            print(OK_MSG)



            '''Test Code Result Enable'''
            print(intro+"Code Result Enable")
            nameG = self.prefix+"-TestCodeResultEnable_RBV"
            nameS = self.prefix+"-TestCodeResultEnable"
            
            value =  waitUntilPV(nameG,0)
            
            print(space+nameG+": "+str(value))
            
            self.assertEqual(value,0,FAIL_MSG)
            print(OK_MSG)


            '''Change Code Result Enable'''
            print(intro+"Change Test Code Result Enable")

            epics.caput(nameS,1,wait= False,timeout=5)
            sleep(2)

            value =  waitUntilPV(nameG,1)
            print(space+nameG+": "+str(value))
             
            self.assertEqual(value,1,FAIL_MSG)
            print(OK_MSG)

           
            '''Test Text Result after changes'''
            print(intro+"Test Text Result after changes")
            nameG = self.prefix+"-TestTxtResult"
            
            value =  epics.caget(nameG,as_string=True)
            
            print(space+nameG+": "+value)
        
            self.assertEqual(value,"Verbose information\nTest ID: 123\nTest TxtID: Test-01\nCodeResult: 1",FAIL_MSG)
            print(OK_MSG)



            '''Signal Quality Flag'''
            print(intro+"Signal Quality Flag")
            nameG = self.prefix+"-SignalQFlag"
            
            value =  waitUntilPV(nameG,0)
            
            print(space+nameG+": "+str(value))
            
            self.assertEqual(value,0,FAIL_MSG)
            print(OK_MSG)

            

            '''Signal Quality Flag Trig Level'''
            print(intro+"Signal Quality Flag Trig Level")
            nameG = self.prefix+"-SignalQFlagTrigLevel_RBV"
            nameS = self.prefix+"-SignalQFlagTrigLevel"
            
            value =  waitUntilPV(nameG,0.5)
            
            print(space+nameG+": "+str(value))
            
            self.assertEqual(value,0.5,FAIL_MSG)
            print(OK_MSG)


            '''Change Signal Quality Flag Trig Level'''
            print(intro+"Change Test Code Result Enable")

            epics.caput(nameS,1.2,wait= False,timeout=5)
            sleep(2)

            value =  waitUntilPV(nameG,1.2)
            print(space+nameG+": "+str(value))
             
            self.assertEqual(value,1.2,FAIL_MSG)
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

            # '''Global RUNNING'''
            # print(intro+"Global ON")
            # value =  epics.caget(nameGG)
            # print(space+nameGG+": "+self.sm_dic.setdefault(value,None))

            # self.assertEqual(value,self.ON,FAIL_MSG)
            # print(OK_MSG)


            '''ON --> OFF'''
            print(intro+"ON --> OFF")
            epics.caput(nameS,self.OFF,wait= False,timeout=5)
            sleep(1)
            
            value =  waitUntilPV(nameG,self.OFF)
            print(space+nameG+": "+self.sm_dic.setdefault(value,None))
            
            self.assertEqual(value,self.OFF,FAIL_MSG)
            print(OK_MSG)

            # '''Global RUNNING'''
            # print(intro+"Global ON")
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
                   "| NDS-SRS-F-1160\n"+
                   "| NDS-SRS-F-1170\n"+
                   "| NDS-SRS-F-1180\n"+
                   "| NDS-SRS-F-1190\n"+
                   "| NDS-SRS-F-1210\n"+
                   "| NDS-SRS-F-1220\n"+
                   "| NDS-SRS-F-1230\n"+
                   "| NDS-SRS-F-1240\n"+
                   "| NDS-SRS-F-1250\n"+
                   "| NDS-SRS-F-1260\n"+
                   "| NDS-SRS-F-1270\n"+
                   "| NDS-SRS-F-1280\n"+
                   "| NDS-SRS-F-1290\n"+
                   "| NDS-SRS-F-1300\n"+
                   self.line,1)


            
            

        except KeyboardInterrupt:
            print("KeyboardInterrupt")
            self.ioc.stop()
            ioc = None
            print("Asserting False-Test interrupted manually")
            self.assertEqual(1,0)

    
       
        
       
if __name__ == '__main__':
    unittest.main()
