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



class TestNdsDeviceDataMultiplexing(ParametrizedTestCase):
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
            libFile = 'libnds3-DeviceDataMultiplexing.so' 
            subsFile = 'DeviceDataMultiplexing.substitutions'
            DeviceName = "B-0"
            DriverName = "DeviceDataMultiplexing"
            
            iocCmd =  self.ioc.iocCommandCompose(appName, libFile,subsFile,DeviceName,DriverName,self.param)
            #print("")
            #print(iocCmd) 

            CBS1 = 'TEST'
            CBS2 = 'FCT0'
            BOARDTYPE = 'B'
            BOARDTYPEIDX='0'
            DMUX_NAME = 'DMUX4'
            
            self.prefix_base =  CBS1+'-'+CBS2\
                +'-HWCF:'+BOARDTYPE+'-'+BOARDTYPEIDX
            self.prefix = self.prefix_base +'-'+ DMUX_NAME

            extra_cmd = "nds subscribe B-0-DataMultiplexing_4_float-DataIn_0 B-0-FloatArray_Source_0\n" +\
                        "nds subscribe B-0-DataMultiplexing_4_float-DataIn_1 B-0-FloatArray_Source_1\n" +\
                        "nds subscribe B-0-DataMultiplexing_4_float-DataIn_2 B-0-FloatArray_Source_2\n" +\
                        "nds subscribe B-0-DataMultiplexing_4_float-DataIn_3 B-0-FloatArray_Source_3\n"
            iocCmd += extra_cmd
            self.ioc.iocProcess.stdin.write(iocCmd)
            sleep(2)
            print(self.line)
            print("|")
            print("|                    TEST DataMultiplexing NODE")
            print("|")
            print(self.line)    
            print("|")
            
            printv("| Check all the PVs related to the Data Multiplexing node:",1)

            printv("|  - State Machine\n"+
                   "|  - Sampling\n"+
                   "|  - Trigger\n"+
                   "|  - Increase Resources\n" +
                   self.line,1)
           
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

    def testMultiplexing(self):
        OKGREEN = '\033[92m'
        FAIL = '\033[91m'
        ENDC = '\033[0m'
        FAIL_MSG = FAIL+"    [FAILED]"+ENDC
        OK_MSG = "|"+OKGREEN+"   [OK]"+ENDC+"\n\n"
        samples = 20
        epics.ca.replace_printf_handler(handle_messages)
        #space = "    "
        intro = "|---"
        space = "|   "
        try:   
            nameG = self.prefix+'-StateMachine-getState'
            nameS = self.prefix + '-StateMachine-setState'
            
            '''Default State'''
            print("|---Default State")
            
            value =  waitUntilPV(nameG, self.OFF)
            print(space+nameG+": "+self.sm_dic[value])

            self.assertEqual(value,self.OFF,FAIL_MSG)
            print(OK_MSG)
            

            '''OFF --> ON'''
            print(intro+"OFF --> ON")
            epics.caput(nameS,self.ON,wait= False,timeout=5)
            value = waitUntilPV(nameG, self.ON)

            print(space+nameG+": "+self.sm_dic[value])
            
            self.assertEqual(value,self.ON,FAIL_MSG)
            print(OK_MSG)

            '''SamplesPerChannel'''
            print(intro+"Sample per Channel")
            
            name = self.prefix+"-SamplesPerChannel"
            name_RBV = name + "_RBV"
            epics.caput(name, samples, wait= False, timeout=5)
            value =  waitUntilPV(name_RBV, samples)
            
            print(space + name + ": " + str(value))
            
            self.assertEqual(value, samples,FAIL_MSG)
            print(OK_MSG)
            
            '''ON --> RUNNING'''
            print(intro+"ON --> RUNNING")
            
            epics.caput(nameS,self.RUNNING,wait= False,timeout=5)
            value = waitUntilPV(nameG, self.RUNNING)

            print(space+nameG+": "+self.sm_dic[value])
            
            self.assertEqual(value,self.RUNNING,FAIL_MSG)
            print(OK_MSG)

            '''IncreaseSources'''
            print(intro+"Increase Sources")
            
            name = self.prefix_base +"-IncreaseSources"
            name_source = self.prefix_base + "-FloatArray_Source_"
            epics.caput(name, 1, wait= False, timeout=5)
            for k in range(4):
                name = name_source + str(k)
                value =  epics.caget(name)
                
                print(space + name + ": " + str(value))
                
                try:
                    table = [value[j] == (k*samples+j) for j in range(samples)]
                    if False not in table:
                        equal = True
                    else:
                        equal = False
                except:
                    equal = False
                self.assertEqual(equal, True, FAIL_MSG)
                print(OK_MSG)
                
            '''Trigger'''
            print(intro + "Trigger")
            
            name = self.prefix +"-Trigger"
            name_dataout = self.prefix + "-DataOut_0"
            epics.caput(name, 1, wait= False, timeout=5)
            
            value =  epics.caget(name_dataout)
            print(space + name_dataout + ": " + str(value))
            asize = samples * 4
            try:
                table = [value[j] == j for j in range(asize)]
                if False not in table:
                    equal = True
                else:
                    equal = False
            except:
                equal = False
            self.assertEqual(equal, True, FAIL_MSG)
            print(OK_MSG)

     
                
            '''RUNNING --> ON'''
            print(intro+"RUNNING --> ON")
            
            nameG = self.prefix+'-StateMachine-getState'
            nameS = self.prefix + '-StateMachine-setState'
            
            epics.caput(nameS,self.ON,wait= False,timeout=5)
            value = waitUntilPV(nameG, self.ON)

            print(space+nameG+": "+self.sm_dic[value])
            
            self.assertEqual(value,self.ON,FAIL_MSG)
            print(OK_MSG)




            '''ON --> OFF'''
            print(intro+"ON --> OFF")
            
            nameG = self.prefix+'-StateMachine-getState'
            nameS = self.prefix + '-StateMachine-setState'
            
            epics.caput(nameS,self.OFF,wait= False,timeout=5)
            value = waitUntilPV(nameG, self.OFF)

            print(space+nameG+": "+self.sm_dic[value])
            
            self.assertEqual(value,self.OFF,FAIL_MSG)
            print(OK_MSG)
            
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
