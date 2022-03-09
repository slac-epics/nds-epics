

#!/usr/bin/env python
'''Controls the test IOC'''
import subprocess
import atexit
import time
import os
import ioctests
from threading import Thread
from time import sleep


def setVerbosityLevel(v):
    global verbosityLevel
    verbosityLevel = v

def printv(msg,v):
    if(verbosityLevel>=v):
        print(msg)
    
class iocControl:
    iocProcess = None
    #DEVNULL = None
    stopping_flag = 1
    iocBoot_path = ""
    
    

    def threaded_function(self):
        '''Thread to read from the pipe'''
        while  self.iocProcess is not None:
            if(self.stopping_flag == 0):
                break
            try:    
                output = self.iocProcess.stdout.readline()
                print('* \033[94m' +output.strip()+'\033[0m')
            except:
                print("Exception: iocControl: exception in the thread function used to read ioc output")
                break
    

    def startIOC(self, arglist=None):
        '''Starts the test IOC'''
        
        relative_path_to_iocBoot_App = '../../examplesTop/iocBoot/iocndsex1/'
        childEnviron = os.environ.copy()

        iocCommand = [ioctests.iocExecutable]

        #retval=os.getcwd()

        #print("Current working directory %s" % retval)
        #print("Changing to iocBoot/xxx")
        path=os.path.dirname(os.path.realpath(relative_path_to_iocBoot_App))

        self.iocBoot_path = path

        os.chdir(path)
	#retval=os.getcwd()
        #print("Current working directory after changing %s" % retval)
 	
        #if ioctests.verbose:
        #    print("Starting the IOC using")
        #    print(iocCommand[0])
       
        '''opening a pipe using subprocess'''
        
        printv("Opening IOC",1)   
        self.iocProcess = subprocess.Popen(iocCommand, 
                                           env=childEnviron,
                                           stdin=subprocess.PIPE, 
                                           stdout=subprocess.PIPE, 
                                           stderr=subprocess.STDOUT,
                                           cwd=path)
         
        printv("IOC opened",1)
        time.sleep(.5)
        
        if(verbosityLevel==2): 
            self.thread = Thread(target = self.threaded_function)
            self.thread.start()
        

        #atexit.register(self.stop)



    def iocCommandCompose(self,appName,libFile,subsFile,DeviceName,DriverName,parameters=""):
        
        TOP_PATH = 'epicsEnvSet("TOP","'+self.iocBoot_path+'/..")'
       
        ENV_EXAMPLE_LIB_PATH= 'epicsEnvSet("EXAMPLE_LIB_PATH", "/opt/codac/lib")'

        EPICS_DB_INCLUDE_PATH = 'epicsEnvSet("EPICS_DB_INCLUDE_PATH",".:$(TOP)/../db:$(EPICS_ROOT)/db:$(TOP)/../nds3-epicsApp/Db")'

        STREAM_PROTOCOL_PATH = 'epicsEnvSet("STREAM_PROTOCOL_PATH","$(TOP)/db:$(EPICS_ROOT)/db")'

        EPICS_BASE_PATH = 'epicsEnvSet("EPICS_BASE","/opt/codac/epics")'

        iocDb= '${TOP}/'+appName+'App/Db'

        iocCmd = TOP_PATH +'\n' \
                + EPICS_BASE_PATH +'\n' \
                + STREAM_PROTOCOL_PATH+'\n' \
                + ENV_EXAMPLE_LIB_PATH+'\n' \
                + EPICS_DB_INCLUDE_PATH+'\n' \
                +'cd .. \n'\
                + 'dbLoadDatabase dbd/'+appName+'.dbd\n'\
                + appName+'_registerRecordDeviceDriver pdbbase\n'\
                + 'ndsLoadDriver $(EXAMPLE_LIB_PATH)/'+libFile+'\n'\
                + 'ndsCreateDevice '+DriverName+' '+DeviceName+" "+parameters+'\n'\
                + 'cd "'+iocDb+'"\n'\
                + 'dbLoadTemplate('+subsFile+')\n'\
                + 'iocInit\n' \
                +'dbl\n'
        printv(iocCmd,1)
       
        return iocCmd



    def stop(self):
        '''Stops the test IOC'''
        printv("Stopping IOC",1)
        if self.iocProcess:
            '''self.iocProcess.stdin.close()'''
           
            self.iocProcess.stdin.write('exit\n')
            self.stopping_flag=0

            #sleep(5) Working if we let it sleeping for 5 seconds, enough time to exit the IOC
            while(self.iocProcess.poll() is None):
                sleep(0.5)
            
            print("Terminating")
            #self.iocProcess.terminate()
            self.iocProcess = None
            if(verbosityLevel==2):
                '''Stops the thread'''
                self.thread.join()
            sleep(2)
        #if self.DEVNULL:
        #    self.DEVNULL.close()


if __name__ == "__main__":
    ioctests.setup()
    print("Running the test IOC in verbose mode for {0} seconds".format(ioctests.iocRunDuration))
    ioctests.verbose = True
    test_iocControl = iocControl()
    test_iocControl.startIOC()
    time.sleep(ioctests.iocRunDuration)
    print("Stopping")
    test_iocControl.stop()
