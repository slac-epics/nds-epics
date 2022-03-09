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



class TestNdsRouting(ParametrizedTestCase): #unittest.TestCase
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
            libFile = 'libnds3-'+'DeviceRouting'+'.so'    #Ex: DeviceVectorDBL
            subsFile = 'Routing'+'.substitutions'          #Ex: WaveForm
            DeviceName = "B-0"                              #Ex: B-0
            DriverName = "DeviceRouting"                   #Ex: DeviceVectorDBL
            CBS1 = 'TEST'
            CBS2 = 'FCT0'
            BOARDTYPE = 'B'
            BOARDTYPEIDX='0'
            NODE_NAME = 'RoutingNode'
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
                   ('ClkSrc'                   ,int(1)        ),#route clocks
                   ('ClkSrcRead'               ,int(1)        ),
                   ('ClkDst'                   ,int(1)        ),
                   ('ClkSet'                   ,int(1)        ),
                   ('ClkSetCode'               ,int(1)        ),             
                   ('ClkSetStatus'             ,int(0)        ),  #Clock Route Status      
                   ('ClkDstRead'               ,int(1)        ),         
                   ('TermSrc'                  ,int(1)        ),                    
                   ('TermDst'                  ,int(1)        ),          
                   ('TermSyncSet'              ,int(1)        ),    
                   ('TermInvertSet'            ,int(1)        ),
                   ('TermSet'                  ,int(1)        ),    
                   ('TermSetCode'              ,int(1)        ),    
                   ('TermSetStatus'            ,int(1)        ),    #Read Routing Configuration
                   ('TermSrcRead'              ,int(1)        ),
                   ('TermDstRead'              ,int(1)        ),
                   ('TermInvertRead'           ,int(1)        ),
                   ('TermSyncRead'             ,int(1)        ),             
                   ('STM-getGlobalState'       ,int(0)        ),    
                   ('STM-getState'             ,int(0)        ),
                   ('STM-setState'             ,int(4)        ),
                   ('ClkSet'                   ,int(0)        ),
                   ('TermDst'                  ,int(0)        ),
                   ('TermSet'                  ,int(0)        ),
                   ('STM-setState'             ,int(1)        ),
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
            print("|                    TEST ROUTING NODE")
            print("|")
            print(self.line)    
            print("|")
            printv("| Test the PVs driver using Python channel access\n|\n"+self.line,1)
            if(self.param == "INIT=YES"):
               
                init_list = [
                    ("ClkDst",-2),
                    ("ClkDstRead",0),                    
                    ("ClkSet",0),
                    ("ClkSrc",-1),
                    ("TermDst",-4),
                    ("TermDstRead",3),
                    ("TermInvertSet",0),
                    ("TermSet",0),                
                    ("TermSrc",-3),
                    ("TermSyncSet",0)]
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
                   "| REQUIREMENTS\n"+
                   "| NDS-SRS-I-0120\n"+
                   "| NDS-SRS-I-0130\n"+
                   "| NDS-SRS-F-1140 \n"+
                   "| NDS-SRS-F-1150 \n"+
                   "| NDS-SRS-F-1520 \n"+
                   "| NDS-SRS-F-1530 \n"+
                   "| NDS-SRS-F-1540 \n"+
                   "| NDS-SRS-F-1550 \n"+
                   "| NDS-SRS-F-1560 \n"+
                   self.line,1)
              
        except KeyboardInterrupt:
            print("KeyboardInterrupt")
            self.ioc.stop()
            ioc = None
            print("Asserting False-Test interrupted manually")
            self.assertEqual(1,0)

    
       
        
       
if __name__ == '__main__':
    unittest.main()

