##!/usr/bin/env python
import sys
import os
import unittest
import epics
from epics import ca
import subprocess
from time import sleep
import iocControl
from iocControl import printv
import ioctests
import numpy as np
#from __builtin__ import iter
from parametrizedTestCase import ParametrizedTestCase
from testUtils import waitUntilPV


def handle_messages(text):
    pass



class TestNdsTrigAndClk(ParametrizedTestCase): #unittest.TestCase
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
    
    sm_dic={UNKNOWN:'UNKNOWN',OFF:'OFF',SWITCH_OFF:'SWITCH_OFF',INITIALIZING:'INITIALIZING',ON:'ON',STOPPING:'STOPPING',STARTING:'STARTING',RUNNING:'RUNNING', FAULT:'FAULT',None:'NONE'}
    
    pvFilePath  = ""
    pvList=[]                                 # self.pvList will be used as the test data holder
    chkList=[]
    tsList = []
    valList = []
    lastCB=''
    monitFlag = 0
    line = "+---------------------------------------------------------------------"
    def monitCallback(self,pvname,*args,**kwds):
        if pvname != 0 :
            if self.lastCB != pvname :
                print("{0:<45},{1:<15},{2}").format(pvname,kwds['value'],epics.pv.fmt_time(kwds['timestamp']))
            self.monitFlag = 1
        else :
            print("error callback pvname")
        self.lastCB=pvname
    
    
    def setUp(self):
        try:
            ioctests.setup()
            ca.initialize_libca()
            epics.ca.replace_printf_handler(handle_messages)
            self.ioc = iocControl.iocControl()
            self.ioc.startIOC()                                           
                                                           
            appName = 'ndsex1'                              #Ex: 
            libFile = 'libnds3-'+'DeviceTrigAndClk'+'.so'    #Ex: DeviceVectorDBL
            subsFile = 'TrigAndClk'+'.substitutions'          #Ex: WaveForm
            DeviceName = "B-0"                              #Ex: B-0
            DriverName = "DeviceTrigAndClk"                   #Ex: DeviceVectorDBL
            CBS1 = 'TEST'
            CBS2 = 'FCT0'
            BOARDTYPE = 'B'
            BOARDTYPEIDX='0'
            NODE_NAME = 'TrigAndClk'
            '''Other test utilities'''
            self.pvFilePath  = os.getcwd()+'/pvList.txt'
            
            arrODATA = 32 * [1]  #Reference datatypes, use same construction on list for easier reading.
            arrZDATA = 32 * [0]
            #a64ODATA = 64 * [1]
            #a64ZDATA = 64 * [0] 
            #intFDATA = int(4)
            #intZDATA = int(0)
            #numODATA = 1.0
            #numZDATA = 0.0
            #strODATA = 'ON'
            #strZDATA = 'OFF'
            floODATA = np.float(1)
            floZDATA = np.float(0)
            npaODATA = np.ndarray([0])
            npaZDATA = np.ndarray([0])
            npaODATA.fill(1)
            npaZDATA.fill(0)
                                                                    
            self.userList=[
                    ('StateMachine-getState'               ,int(0)   ),
                    ('StateMachine-setState'               ,int(4)   ),
                    ('ResetTrigConf'                       ,int(0)   ),
                    ('SetSW'                               ,int(0)   ),
                    ('Change'                              ,int(1)   ),
                    ('Change_RBV'                          ,int(0)   ),
                    ('DAQStartTimeDelay'                   ,int(1)   ),
                    ('DAQStartTimeDelay_RBV'               ,int(0)   ), 
                    ('Edge'                                ,int(1)    ),
                    ('Edge_RBV'                            ,int(0)   ),
                    ('HWBlock'                             ,int(1)   ),
                    ('HWBlock_RBV'                         ,int(0)   ),
                    ('Level'                               ,int(1)    ),
                    ('Level_RBV'                           ,int(0)   ),
                    ('Mode'                                ,int(1)   ),
                    ('Mode_RBV'                            ,int(0)   ),
                    ('ClkDivider'                          ,int(1)   ),
                    ('ClkDivider_RBV'                      ,int(0)   ),
                    ('TrigPeriod'                          ,int(1)   ),
                    ('TrigPeriod_RBV'                      ,int(0)   ),
                    ('PostTrigSamples'                     ,int(100)   ),
                    ('PostTrigSamples_RBV'                 ,int(0)   ),
                    ('PreTrigSamples'                      ,int(100)   ),
                    ('PreTrigSamples_RBV'                  ,int(0)   ),
                    ('LoadTrigConf'                        ,int(1)   ),
                    ('TrigLoadCode'                        ,int(0)   ),
                    ('TrigLoadStatus'                      ,"wrong"   ),
                    ('SetSW'                               ,int(1)   ),
                    ('PLLSyncSET'                          ,int(0)   ),
                    ('EnableDisablePLL'                    ,int(0)   ),
                    ('PLLRefDiv'                           ,int(1)   ),
                    ('PLLRefDiv_RBV'                       ,int(0)   ),
                    ('PLLRefDivALL'                        ,int(10101)   ),
                    ('PLLRefDivALL_RBV'                    ,int(0)   ),
                    ('PLLRefFreq'                          ,int(1)   ),
                    ('PLLRefFreq_RBV'                      ,int(0)   ),
                    ('PLLRefMult'                          ,int(1)   ),
                    ('PLLRefMult_RBV'                      ,int(0)   ),
                    ('SyncMode'                            ,int(1)   ),
                    ('SyncMode_RBV'                        ,int(0)   ),
                    ('PLLSyncSET'                          ,int(1)   ),
                    ('PLLLoadCode'                         ,int(0)   ),
                    ('PLLLoadStatus'                       ,"wrong"   ),
                    ('EnableDisablePLL'                    ,int(1)   ),
                    ('EnableDisablePLL_RBV'                ,int(0)   ),
                    ('Route-ClkSrc'                   ,int(1)        ),
                    ('Route-ClkDst'                   ,int(1)        ),
                    ('Route-ClkSet'                   ,int(1)        ),
                    ('Route-ClkSetCode'               ,int(1)        ),
                    ('Route-ClkSetStatus'             ,int(0)        ),
                    ('Route-ClkDstRead'               ,int(1)        ),
                    ('Route-TermSrc'                  ,int(1)        ),
                    ('Route-TermDst'                  ,int(1)        ),
                    ('Route-TermSyncSet'              ,int(1)        ),
                    ('Route-TermInvertSet'            ,int(1)        ),
                    ('Route-TermSet'                  ,int(1)        ),
                    ('Route-TermSetCode'              ,int(1)        ),
                    ('Route-TermSetStatus'            ,"wrong"       ),
                    ('Route-TermSrcRead'              ,int(1)        ),
                    ('Route-TermDstRead'              ,int(1)        ),
                    ('Route-TermInvertRead'           ,int(1)        ),
                    ('Route-TermSyncRead'             ,int(1)        ),
                    ('Route-STM-getGlobalState'       ,int(0)        ),
                    ('Route-STM-getState'             ,int(0)        ),
                    ('Route-STM-setState'             ,int(4)        ),
                    ('Route-ClkSet'                   ,int(0)        ),
                    ('Route-TermDst'                  ,int(0)        ),
                    ('Route-TermSet'                  ,int(0)        ),
                    ('Route-STM-setState'             ,int(1)        )
            
                     ]
            

            
            iocCmd =  self.ioc.iocCommandCompose(appName, libFile,subsFile,DeviceName,DriverName,self.param)
            #print("")
            #print(iocCmd) 
            
            self.ioc.iocProcess.stdin.write(iocCmd)
            sleep(1)
            self.ioc.iocProcess.stdin.write('dbl >'+ self.pvFilePath +'\n')
            self.ioc.iocProcess.stdin.flush()
            sleep(1)
            with open(self.pvFilePath) as m_file :
                self.pvList = m_file.readlines()
            self.prefix = CBS1+'-'+CBS2\
                +'-HWCF:'+BOARDTYPE+'-'+BOARDTYPEIDX+'-'+NODE_NAME+'-'    
            print("+---------------------------------------------------------------------")
            print("|                    CHECKING TESTS")
            print("+---------------------------------------------------------------------")    
            print("|")
            '''------------------------check if userList constains pvList--------------'''    
            for i in range(len(self.userList)):
                self.chkList.insert(i,self.prefix+str(self.userList[i][0]))
                #print(i, self.chkList[i]) #debug
            for i in range(len(self.pvList)):
                self.pvList[i]=self.pvList[i].strip()
                #print (i,self.pvList[i]) #debug
            chkSet=set(self.pvList).difference(set(self.chkList))
            if len(chkSet) != 0:
                i=0
                while(chkSet!= set()):
                    print (i, chkSet.pop(),'Warning! PV not in test cases!')
                    i=i+1    
            '''------------------------rename to list for easier coding----------------'''
            del self.pvList[:]
            del self.valList[:]
            for i in range(len(self.userList)) :
                self.pvList.insert(i, self.prefix+self.userList[i][0])
                self.valList.insert(i, self.userList[i][1])
         
            self.pvFilePath   
            self.pvList                                 # self.pvList will be used as the test data holder
            self.chkList
            self.tsList
            self.valList
            
          
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
        os.remove(self.pvFilePath)
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
            '''-----------------------Define custom test procedure---------------------'''
            print("+---------------------------------------------------------------------")
            print("|                    Listing PVs")
            print("+---------------------------------------------------------------------")    
            print("|")
            for i in range(len(self.pvList)) :
    #            a = self.pvList[i].strip()
    #            self.pvList[i] = a.strip()
                self.tsList.append(epics.pv.get_pv(self.pvList[i],connect=True)._getarg('timestamp'))
                print("{0:>3},{1:<60},{2:12}".format(i,   self.pvList[i], epics.pv.fmt_time(self.tsList[i]))) 
                ca.poll()
            '''caget PV list....'''
            readbacks = epics.caget_many(self.pvList)
            ca.poll(1,1)
            for i in range(len(self.pvList)) : 
                self.tsList[i]=epics.pv.get_pv(self.pvList[i],connect=True,timeout=5)._getarg('timestamp')
                print("{0:<45},{1:12}".format(self.pvList[i], epics.pv.fmt_time(self.tsList[i]))) 
                print("{0:<15},{1:<60}".format(type(readbacks[i]), readbacks[i])) 

            print(self.line)
            print("|")
            print("|                    TEST Trigger and Clock NODE")
            print("|")
            print(self.line)    
            print("|")
            printv("| Test the PVs driver using Python channel access\n|\n"+self.line,1)
            if(self.param == "INIT=YES"):
               
                init_list = [
                    ('SetSW',   1),
                    ('HWBlock', 0),
                    ('LoadTrigConf',   0),
                    ('DAQStartTimeDelay', 0),
                    ('TrigPeriod', 0),
                    ('Level', 0),
                    ('Edge', 0),
                    ('Change', 0),
                    ('Mode', 0),
                    ('PreTrigSamples', 1),
                    ('PostTrigSamples', 1),
                    ('PLLSyncSET', 1),
                    ('SyncMode', 0),
                    ('PLLRefFreq', 0),
                    ('PLLRefDiv', 0),
                    ('PLLRefMult', 0),
                    ('PLLRefDivALL', 1),
                    ('EnableDisablePLL', 0),
                    ('ResetTrigConf', 1)]
                printv("| Check the initialization PVs values:",1)
                for name,v in init_list:
                    printv("|  - "+name,1)
                    
                for item in init_list:       
                     nameS = self.prefix+item[0]
                     value =  waitUntilPV(nameS,item[1])
                     print(space+nameS+": "+str(value))
                     self.assertEqual(value,item[1],FAIL_MSG)
                print(OK_MSG)
            for i in range(len(self.pvList)):
                epics.camonitor(self.pvList[i], None, self.monitCallback)
            for i in range(len(self.pvList)) : 
                print("---caput---->  " + str(self.pvList[i]).replace(str(self.pvList[i])[:len(self.prefix)], ''))
                epics.caput(self.pvList[i], self.valList[i] , wait=True, timeout=5)
                sleep(0.3)
                ca.poll(1,1)
                if self.monitFlag == 0:
                    print("Timeout: "+ str(self.pvList[i]))
                self.monitFlag = 0
                print("+---------------------------------------------------------------------")
            print("+---------------------------------------------------------------------")
            
            readbacks = epics.caget_many(self.pvList)
            ca.poll(1,1)
    #        for i in range(len(self.pvList)) : 
    #            for j in range(len(DATATYPES)) :
    #                if type(DATATYPES[j]) == type(readbacks[i]) : 
    #                    vallist.append(DATATYPES[j]) 
            nErr=0
            for i in range(len(self.pvList)) : 
                if self.tsList[i] == epics.pv.get_pv(self.pvList[i],connect=True,timeout=5)._getarg('timestamp') :
                    print("{0:<11},{1:<45},{2}".format(FAIL_MSG,self.pvList[i], epics.pv.fmt_time(self.tsList[i]))) #debug  
                    #self.assertEqual(nErr, 0,FAIL_MSG+str(self.pvList[i])+str(epics.pv.fmt_time(self.tsList[i])))
                    nErr=nErr+1
                
    
            print("Total number of not updated PVs:"+str(nErr))
            print("Total number of tests:          "+str(len(self.pvList))) 
            print("Total number of timestamps:     "+str(len(self.tsList)))
            self.assertEqual(nErr, 0,FAIL_MSG +str(nErr)+'tests')
            print(OK_MSG)       
            #print("+------------------TEST RELATED REQUIREMENT LIST: \n------------------")
            printv(self.line+"\n"+
                   "NDS-SRS-F-0730 \n"+
                   "NDS-SRS-F-0740 \n"+
                   "NDS-SRS-F-0750 \n"+
                   "NDS-SRS-F-0760 \n"+
                   "NDS-SRS-F-0770 \n"+
                   "NDS-SRS-F-0780 \n"+
                   "NDS-SRS-F-0790 \n"+
                   "NDS-SRS-F-0800 \n"+
                   "NDS-SRS-F-0810 \n"+
                   "NDS-SRS-F-0820 \n"+
                   "NDS-SRS-F-0830 \n"+
                   "NDS-SRS-F-0840 \n"+
                   "NDS-SRS-F-0850 \n"+
                   "NDS-SRS-F-0860 \n"+
                   "NDS-SRS-F-0870 \n"+
                   self.line,1)
            
            
        except KeyboardInterrupt:
            print("KeyboardInterrupt")
            self.ioc.stop()
            ioc = None
            print("Asserting False-Test interrupted manually")
            self.assertEqual(1,0)

    
       
        
       
if __name__ == '__main__':
    unittest.main()

