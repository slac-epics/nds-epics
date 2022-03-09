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



class TestNdsFirmware(ParametrizedTestCase):
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
            libFile = 'libnds3-DeviceFirmware.so' 
            subsFile = 'Firmware.substitutions'
            DeviceName = "B-0"
            DriverName = "DeviceFirmware"
            
            iocCmd =  self.ioc.iocCommandCompose(appName, libFile,subsFile,DeviceName,DriverName,self.param)
            #print("")
            #print(iocCmd) 
            
            self.ioc.iocProcess.stdin.write(iocCmd)
            sleep(2)
            print(self.line)
            print("|")
            print("|                    TEST FIRMWARE NODE")
            print("|")
            print(self.line)    
            print("|")
            
            printv("| Check all the PVs related with initial Firmware node configuration:",1)
            if(self.param == "INIT=YES"):
                extra = "| Initial default value\n"
            else:
                extra = ""
            printv("|  - Version\n"+
                   "|  - Status\n"+
                   "|  - HWRevision\n"+
                   "|  - SerialNumber\n"+
                   "|  - Model\n"+
                   "|  - Type\n"+
                   "|  - DriverVersion\n"+
                   "|  - ChassisNumber\n"+
                   "|  - SlotNumber\n"+
                   "|  - FilePath\n"+
                   "| Test modifications of firmware file path PV\n"+
                   "| Check the transitions of state machine\n"+
                   extra+
                   "|\n"+
                   self.line,1)
            

            CBS1 = 'TEST'
            CBS2 = 'FCT0'
            BOARDTYPE = 'B'
            BOARDTYPEIDX='0'
            FIRMWARE_NAME = 'Firm'
            

            self.prefix = CBS1+'-'+CBS2\
                +'-HWCF:'+BOARDTYPE+'-'+BOARDTYPEIDX+'-'+FIRMWARE_NAME    
           
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

            # if(self.param == "INIT=YES"):
            #     '''Testing Initialization'''
            #     print("|---Default Initialization no RBV")
            #     nameS = self.prefix+"-FilePath"
            #     value =  epics.caget(nameS)
            #     print(space+nameS+": "+str(value))
            #     self.assertEqual(value,"not available",FAIL_MSG)


            nameG = self.prefix+'-StateMachine-getState'
            nameS = self.prefix + '-StateMachine-setState'
            nameGG = self.prefix + '-StateMachine-getGlobalState'
            
            '''Default State'''
            print("|---Default State")
            
            value =  waitUntilPV(nameG,self.OFF)
            print(space+nameG+": "+self.sm_dic[value])

            self.assertEqual(value,self.OFF,FAIL_MSG)
            print(OK_MSG)
            

            # ''' Default Global '''
            # print(intro+"Default Global State")
            # value =  epics.caget(nameGG)
            # print(space+nameGG+": "+self.sm_dic[value])

            # self.assertEqual(value,self.OFF,FAIL_MSG)
            # print(OK_MSG)


            '''OFF --> ON'''
            print(intro+"OFF --> ON")
            epics.caput(nameS,self.ON,wait= False,timeout=5)
            sleep(2)
            
            value =  waitUntilPV(nameG,self.ON)
            print(space+nameG+": "+self.sm_dic[value])
            
            self.assertEqual(value,self.ON,FAIL_MSG)
            print(OK_MSG)
            
            # '''Global ON'''
            # print(intro+"Global ON")
            
            # value =  epics.caget(nameGG)
            # print(space+nameGG+": "+self.sm_dic[value])

            # #self.assertEqual(value,self.ON,FAIL_MSG)
            # print(OK_MSG)

            
            '''VERSION'''
            print(intro+"VERSION")
            nameG = self.prefix+"-Version"
            
            value =  epics.caget(nameG,as_string=True)
            
            print(space+nameG+": "+value)
            
            self.assertEqual(value,"Firmware test version",FAIL_MSG)
            print(OK_MSG)


            '''STATUS'''
            print(intro+"STATUS")
            nameG = self.prefix+"-Status"
            
            value =  waitUntilPV(nameG,0)
            
            print(space+nameG+": "+str(value))
            
            self.assertEqual(value,0,FAIL_MSG)
            print(OK_MSG)


            '''HW Revision'''
            print(intro+"HW Revision")
            nameG = self.prefix+"-HWRevision"
            
            value =  epics.caget(nameG,as_string=True)
            
            print(space+nameG+": "+value)
            
            self.assertEqual(value,"Firmware test hardware revision",FAIL_MSG)
            print(OK_MSG)


            '''Serial Number'''
            print(intro+"Serial Number")
            nameG = self.prefix+"-SerialNumber"
            
            value =  epics.caget(nameG,as_string=True)
            
            print(space+nameG+": "+value)
            
            self.assertEqual(value,"Firmware test serial number",FAIL_MSG)
            print(OK_MSG)


            '''Firmware Model'''
            print(intro+"Firmware Model")
            nameG = self.prefix+"-Model"
            
            value =  epics.caget(nameG,as_string=True)
            
            print(space+nameG+": "+value)
            
            self.assertEqual(value,"Firmware test device model",FAIL_MSG)
            print(OK_MSG)


            '''Firmware Type'''
            print(intro+"Firmware Type")
            nameG = self.prefix+"-Type"
            
            value =  epics.caget(nameG,as_string=True)
            
            print(space+nameG+": "+value)
            
            self.assertEqual(value,"Firmware test device type",FAIL_MSG)
            print(OK_MSG)


            '''Driver Version'''
            print(intro+"Driver Version")
            nameG = self.prefix+"-DriverVersion"
            
            value =  epics.caget(nameG,as_string=True)
            
            print(space+nameG+": "+value)
            
            self.assertEqual(value,"<major_id>.<minor_id>.<maintenance_id>",FAIL_MSG)
            print(OK_MSG)



            '''CHASSIS NUMBER'''
            print(intro+"Chassis Number")
            nameG = self.prefix+"-ChassisNumber"
            
            value =  waitUntilPV(nameG,42)
            
            print(space+nameG+": "+str(value))
            
            self.assertEqual(value,42,FAIL_MSG)
            print(OK_MSG)



            '''SLOT NUMBER'''
            print(intro+"Slot Number")
            nameG = self.prefix+"-SlotNumber"
            
            value = waitUntilPV(nameG,42)
            
            print(space+nameG+": "+str(value))
            
            self.assertEqual(value,42,FAIL_MSG)
            print(OK_MSG)


            '''FILE PATH'''
            print(intro+"File Path")
            nameG = self.prefix+"-FilePath_RBV"
            
            value =  epics.caget(nameG,as_string=True)
            
            print(space+nameG+": "+value)
            
            self.assertEqual(value,"Firmware path to be uploaded",FAIL_MSG)
            print(OK_MSG)


            '''CHANGE FILE PATH'''
            print(intro+"Change Firmware File Path")
            nameG = self.prefix+"-FilePath_RBV"
            nameS = self.prefix+"-FilePath"
            
            epics.caput(nameS,"New FirmwarePath",wait= False,timeout=5)
            sleep(2)
            value =  epics.caget(nameG,as_string=True)
            
            print(space+nameG+": "+value)
            
            self.assertEqual(value,"New FirmwarePath",FAIL_MSG)
            print(OK_MSG)

            
            '''ON --> OFF'''
            print(intro+"ON --> OFF")
            
            nameG = self.prefix+'-StateMachine-getState'
            nameS = self.prefix + '-StateMachine-setState'
            
            epics.caput(nameS,self.OFF,wait= False,timeout=5)
            value = waitUntilPV(nameG,self.OFF)
            print(space+nameG+": "+self.sm_dic[value])
            
            self.assertEqual(value,self.OFF,FAIL_MSG)
            print(OK_MSG)
            
            printv(self.line+
                   "\n| REQUIREMENTS\n"+
                   "| NDS-SRS-I-0120\n"+
                   "| NDS-SRS-I-0130\n"+
                   "| NDS-SRS-F-1140\n"+
                   "| NDS-SRS-F-1150\n"+
                   "| NDS-SRS-F-1310\n"+
                   "| NDS-SRS-F-1320\n"+
                   "| NDS-SRS-F-1330\n"+
                   "| NDS-SRS-F-1340\n"+
                   "| NDS-SRS-F-1350\n"+
                   "| NDS-SRS-F-1360\n"+
                   "| NDS-SRS-F-1580\n"+
                   "| NDS-SRS-F-1590\n"+
                   "| NDS-SRS-F-1600\n"+
                   self.line,1)
            
            


            
            

        except KeyboardInterrupt:
            print("KeyboardInterrupt")
            self.ioc.stop()
            ioc = None
            print("Asserting False-Test interrupted manually")
            self.assertEqual(1,0)

    
       
        
       
if __name__ == '__main__':
    unittest.main()
