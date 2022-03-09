#!/usr/bin/env python
import unittest
import epics
from epics import ca
import subprocess
from time import sleep
import iocControl
from iocControl import printv
import ioctests
import numpy as np
from parametrizedTestCase import ParametrizedTestCase
from testUtils import waitUntilPV

def handle_messages(text):
    pass



class TestNdsDevicePVs(ParametrizedTestCase):
    '''Testing basic load and initialization of NDS driver in EPICS'''
    ''' 1-setup
    2-test***
    3-tearDown
    '''
    
    prefix =""
    ioc= None
    UNKNOWN = 0
    # OFF = 1
    # SWITCH_OFF = 2
    # INITIALIZING = 3
    # ON = 4
    # STOPPING = 5
    # STARTING = 6
    # RUNNING = 7
    # FAULT = 8
    
    # NOT_SYNCED = 0
    # SYNCING = 1
    # SYNCED = 2
    # LOST_SYNC = 3


    intData = 1
    int64Data = 1
    floatData = 1.5
    doubleData = 1.1
    boolArrayData = np.array([1, 1, 0, 1])
    uInt8ArrayData = np.array([0,1,2])
    uInt16ArrayData = np.array([3,4])
    uInt32ArrayData = np.array([5,6,7])
    int8ArrayData = np.array([0,-1,2])
    int16ArrayData = np.array([3,-4])
    int32ArrayData = np.array([-5,6,-7])
    int64ArrayData = np.array([-8,6,-9])
    floatArrayData = np.array([-0.5,0.5,2.5])
    doubleArrayData = np.array([-0.1,0.2,1.5])
    stringData = "text"
    timespecData = np.array([11111111,2243354])
    timespecArrayData = np.array([1,2, 3,4])
    timestampData = np.array([10,1, 0, 1])

    intDataNew = 5
    int64DataNew = 7
    floatDataNew = 3.5
    doubleDataNew = 4.3
    boolArrayDataNew = np.array([0, 1])
    uInt8ArrayDataNew = np.array([2,1])
    uInt16ArrayDataNew = np.array([1,2])
    uInt32ArrayDataNew = np.array([0,6,5])
    int8ArrayDataNew = np.array([-1,-2])
    int16ArrayDataNew = np.array([-3,4])
    int32ArrayDataNew = np.array([-5,6,32])
    int64ArrayDataNew = np.array([-8,6,3])
    floatArrayDataNew = np.array([-2.5,3.5])
    doubleArrayDataNew = np.array([-1.5,2.4])
    stringDataNew = "newText"
    timespecDataNew = np.array([10,25])
    timespecArrayDataNew = np.array([3,4,10,2])
    timestampDataNew = np.array([1000,10, 1, 1])

    line = "+---------------------------------------------------------------------"

    
    #sm_dic = {UNKNOWN:'UNKNOWN',OFF:'OFF',SWITCH_OFF:'SWITCH_OFF',INITIALIZING:'INITIALIZING',ON:'ON',STOPPING:'STOPPING',STARTING:'STARTING',RUNNING:'RUNNING', FAULT:'FAULT',None:'NONE'}
    #tm_dic ={NOT_SYNCED:"NOT_SYNCED",SYNCING:"SYNCING",SYNCED:"SYNCED", LOST_SYNC:" LOST_SYNC"}

    def setUp(self):
        try:
            ioctests.setup()
            ca.initialize_libca()
            epics.ca.replace_printf_handler(handle_messages)
            self.ioc = iocControl.iocControl()
            self.ioc.startIOC() 
            
            appName = 'ndsex1'
            libFile = 'libnds3-DevicePVs.so' 
            subsFile = 'DevicePVs.substitutions'
            DeviceName = "B-0"
            DriverName = "DevicePVs"

            iocCmd =  self.ioc.iocCommandCompose(appName, libFile,subsFile,DeviceName,DriverName,self.param)
            #print("")
            #print(iocCmd) 
            
            self.ioc.iocProcess.stdin.write(iocCmd)
            sleep(2)
            
            print(self.line)
            #print("|")
            print("|")
            print("|                    TEST DEVICE PVs")
            print("|")
            #print("|")
            print(self.line)    
            print("|")
            printv("| Test all types of supported PV using Python channel access\n|\n"+self.line,1)
            if(self.param == "INIT=YES"):
                printv("| Initialization no RBV\n"+
                       "|  - Integer \n"+
                       "|  - Double\n",1)
            CBS1 = 'TEST'
            CBS2 = 'FCT0'
            BOARDTYPE = 'B'
            BOARDTYPEIDX='0'
            DEVICEPV_NAME = 'DevicePVs'
            

            self.prefix = CBS1+'-'+CBS2\
                +'-HWCF:'+BOARDTYPE+'-'+BOARDTYPEIDX+'-'+DEVICEPV_NAME 
           
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

        PVs = ["Integer",
               "Integer64",
               "Float", #--not supported asynDriver
               "Double",
               "BoolArray",
               "UInt8Array",
               "UInt16Array",
               "UInt32Array",
               #"Int8Array", --not supported pyepics
               "Int16Array",
               "Int32Array",
               "Int64Array",
               "FloatArray",
               "DoubleArray",
               "String",
               "Timespec",
               "TimespecArray",
               "Timestamp"]
        asynType ={"Integer":"(asynInt32)-LONG",
                   "Integer64":"(asynInt64)",
                   "Float":"(asynFloat64)",
                   "Double":"(asynFloat64)",
                   "BoolArray":"(asynInt32Array)-LONG",
                   "UInt8Array":"(asynInt8Array)-UCHAR",
                   "UInt16Array":"(asynInt16Array)-SHORT", 
                   "UInt32Array":"(asynInt32Array)-LONG",
                   "Int8Array":"(asynInt8Array)-CHAR",
                   "Int16Array":"(asynInt16Array)-SHORT",
                   "Int32Array":"(asynInt32Array)-LONG",
                   "Int64Array":"(asynInt64Array)-INT64",
                   "FloatArray":"(asynFloat32Array)",
                   "DoubleArray":"(asynFloat64Array)",
                   "String":"(asynInt8Array)-CHAR",
                   "Timespec":"(asynInt32Array)-LONG",
                   "TimespecArray":"(asynInt32Array)-LONG",
                   "Timestamp":"(asynInt32Array)-LONG"}
        
        default_ini_values = {"Integer":self.intData,
                              "Integer64":self.int64Data,
                              "Float":self.floatData,
                              "Double":self.doubleData,
                              "BoolArray":self.boolArrayData, 
                              "UInt8Array":self.uInt8ArrayData,
                              "UInt16Array":self.uInt16ArrayData,
                              "UInt32Array":self.uInt32ArrayData,
                              "Int8Array":self.int8ArrayData,
                              "Int16Array":self.int16ArrayData,
                              "Int32Array":self.int32ArrayData,
                              "Int64Array":self.int64ArrayData,
                              "FloatArray":self.floatArrayData,
                              "DoubleArray":self.doubleArrayData,
                              "String":self.stringData,
                              "Timespec":self.timespecData,
                              "TimespecArray":self.timespecArrayData,
                              "Timestamp":self.timestampData}
        
        put_values = {"Integer":self.intDataNew,
                      "Integer64":self.int64DataNew,
                      "Float":self.floatDataNew,
                      "Double":self.doubleDataNew,
                      "BoolArray":self.boolArrayDataNew,
                      "UInt8Array":self.uInt8ArrayDataNew,
                      "UInt16Array":self.uInt16ArrayDataNew,
                      "UInt32Array":self.uInt32ArrayDataNew,
                      "Int8Array":self.int8ArrayDataNew,
                      "Int16Array":self.int16ArrayDataNew,
                      "Int32Array":self.int32ArrayDataNew,
                      "Int64Array":self.int64ArrayDataNew,
                      "FloatArray":self.floatArrayDataNew,
                      "DoubleArray":self.doubleArrayDataNew,
                      "String":self.stringDataNew,
                      "Timespec":self.timespecDataNew,
                      "TimespecArray":self.timespecArrayDataNew,
                      "Timestamp":self.timestampDataNew} 

        if(self.param == "INIT=YES"):
                '''Testing Initialization'''
                print("|---Default Initialization no RBV")

                nameS = self.prefix+"-Integer"
                value =  waitUntilPV(nameS,-2147483648)
                print(space+nameS+": "+str(value))
                self.assertEqual(value,-2147483648,FAIL_MSG)
        
                nameS = self.prefix+"-Integer64"
                value =  waitUntilPV(nameS,-9223372036854775808)
                print(space+nameS+": "+str(value))
                self.assertEqual(value,-9223372036854775808,FAIL_MSG)

                nameS = self.prefix+"-Double"
                value =  waitUntilPV(nameS,5e8)
                print(space+nameS+": "+str(value))
                self.assertEqual(value,5e8,FAIL_MSG)


        def test_pv(typePV,expected):
            
            print(intro+typePV+"_RBV "+asynType[typePV])
            nameG = self.prefix+'-'+typePV+'_RBV'
            if(typePV=="String"):
                value =  epics.caget(nameG,as_string=True)
            else:
                value =  epics.caget(nameG)
            print(space+nameG+": "+str(value))
            print(space+"Expected: "+str(expected[typePV]))
            
            
            if (not typePV=="Integer" and not typePV=="Integer64" and not typePV=="Float" and not typePV=="Double" and not typePV=="String"):
                value = value.tolist()
                expected_value = expected[typePV].tolist()
            else:
                expected_value = expected[typePV]
            
            result = [value,expected_value]
            return result
           



        def put_pv(typePV,values):
            try:
                print(intro+typePV+" "+asynType[typePV])
                nameS =  self.prefix+'-'+typePV

                epics.caput(nameS,values[typePV],wait= False,timeout=5)
                sleep(1)
            except KeyboardInterrupt:
                print("KeyboardInterrupt. Finalizing.")
                if self.ioc is not None:
                    self.ioc.stop() 
            except:
                print("Unexpected exception in put_pv")
                if self.ioc is not None:
                    self.ioc.stop()
                raise 
            
        try:   
            
            for PV in PVs:
                value,expected = test_pv(PV, default_ini_values)
                self.assertEqual(value,expected,FAIL_MSG)
                print(OK_MSG) 
                
            for PV in PVs:  
                 put_pv(PV,put_values)
            
                 value,expected = test_pv(PV, put_values)
                 self.assertEqual(value,expected,FAIL_MSG)
                 print(OK_MSG) 
                 
            printv(self.line+"\n| REQUIREMENTS\n| NDS-SRS-I-0120\n| NDS-SRS-I-0130\n"+self.line,1)
            

        except KeyboardInterrupt:
            print("KeyboardInterrupt")
            self.ioc.stop()
            ioc = None
            print("Asserting False-Test interrupted manually")
            self.assertEqual(1,0)

    
       
        
       
if __name__ == '__main__':
    unittest.main()
