 #!/usr/bin/env python
import unittest
from testNdsStateMachine  import TestNdsStateMachine
from testNdsFirmware import TestNdsFirmware 
from testNdsTiming import  TestNdsTiming
from testNdsHQMonitor import TestNdsHQMonitor
from testNdsDevicePVs import TestNdsDevicePVs
from testNdsDataAcquisition import TestNdsWaveformGeneration as TestNdsDataAcquisition
from testNdsDigitalIO import TestNdsDigitalIO
from testNdsFTE import TestNdsFTE
from testNdsTimestamping import TestNdsTimestamping
from testNdsRouting import TestNdsRouting
from testNdsPVTimestamps import TestNdsPVTimestamps
from testNdsTriggerAndClk import TestNdsTrigAndClk
from testNdsReporterAndParser import TestNdsReporterAndParser
from testNdsDeviceDataMultiplexing import  TestNdsDeviceDataMultiplexing
from testNdsError import TestNdsError
import sys
from iocControl import  setVerbosityLevel

from  parametrizedTestCase import ParametrizedTestCase


if __name__ == '__main__':
    from time import sleep    
    
    dict_tests = {"TestNdsStateMachine":TestNdsStateMachine,
                  "TestNdsDataAcquisition":TestNdsDataAcquisition,
                  "TestNdsDigitalIO":TestNdsDigitalIO,
                  "TestNdsFTE":TestNdsFTE,
                  "TestNdsRouting": TestNdsRouting,
                  "TestNdsFirmware":TestNdsFirmware,
                  "TestNdsHQMonitor":TestNdsHQMonitor,
                  "TestNdsTiming":TestNdsTiming,
                  "TestNdsTimestamping":TestNdsTimestamping,
                  "TestNdsDevicePVs":TestNdsDevicePVs,
                  "TestNdsTrigAndClk":TestNdsTrigAndClk,
                  "TestNdsReporterAndParser":TestNdsReporterAndParser,
                  "TestNdsPVTimestamps":TestNdsPVTimestamps,
                  "TestNdsDeviceDataMultiplexing": TestNdsDeviceDataMultiplexing,
                  "TestNdsError": TestNdsError
                  }

    tests = []
    
    VLevels =[0,1,2]
    verbosityLevel=0
    setVerbosityLevel(verbosityLevel)
    opt_param = ""
    def usage():
        print("+---------------------------------------------+")
        print(" USAGE")
        print("")
        print(" No option")
        print("       run all tests")
        print("")
        print("")
        print(" -h") 
        print("       help for this program")
        print("")
        print("")
        print(" -i") 
        print("       Create the Device with INIT=YES")
        print("")
        print("")
        print(" -v [LEVEL]")
        print("       Add verbosity depending of the LEVEL")
        print("       where LEVEL can be 0 (default) 1 or 2")
        print("       LEVEL 1 prints test description and requirement")
        print("       LEVEL 2 prints the IOC messagges")
        print("")
        print("")
        print(" -t [TEST1 TEST2 ... TETSN]")
        print("      run only TEST1, TEST2, ..., TESTN")
        print("")
        print("       Avaliable tests:")
        for test in dict_tests.keys():
            print("       "+test)

        print("") 
        print("")
        print("+---------------------------------------------+")


    def arg_parser_error(msg):
        print(msg)
        usage()
        sys.exit(2) 

    err_format_msg = "\n***Wrong argument format!***\n"
    set_test_wanted = set([])
    list_test_wanted =[]
    
    
    # PARSING
    if (sys.argv[1:]):

        args_str = " ".join(sys.argv[1:]).strip()
        args_str = args_str.replace("-h","-h None ")
        args_str = args_str.replace("-i","-i None ")
    
        #check if first character is "-"
        if(args_str[0]!="-"):
            arg_parser_error(err_format_msg) 

        list_opt = args_str.split("-")

       
        #Remove spurious empty strings
        list_opt = [x for x in list_opt if x!=""]

        #check that the user inserted the pattern -o arg1 arg2
        for item in list_opt:
            
            if(len(item)<3 or item[1]!=" "):
                    print("check that the user inserted the pattern -o arg1 arg2")
                    arg_parser_error(err_format_msg)
                
                
        list_opt = [(x[0],x[1:].strip()) for x in list_opt]

       
        for option, a in list_opt:
            #print(option,a)
            if option == "v":
                if(not a.isdigit()):
                    arg_parser_error("\nVerbosity: Wrong argument format!\n")

                if(int(a) not in VLevels):
                    arg_parser_error("\nVerbosity: Wrong Verbosity Level!\n")
                    

                verbosityLevel = int(a)
                setVerbosityLevel(verbosityLevel)
                
            elif option in ("h"):
                usage()
                sys.exit()
            elif option in ("i"):
               opt_param="INIT=YES"
            elif option in ("t"):
                
                list_test_wanted = a.split()
                set_test_wanted = set(list_test_wanted)
                #print(set_test_wanted)
            else:
                print("Option:",option)
                arg_parser_error(err_format_msg)
                #assert False, "unhandled option"
                

    
    
    
    if(not set_test_wanted):
        ''' if no arguments is given, ie. the set is empty, 
        is intended that we want to execute all the tests'''
        tests = list( dict_tests.values())
        
    else:
        set_dic_tests = set( dict_tests.keys())
        
        if not set_test_wanted.issubset(set_dic_tests):
            '''Check that the user asked for a correct test name'''
            print("ERROR. The following tests are not implemented: ")
            for test in set_test_wanted.difference(set_dic_tests):
                print(test)
            print("Type -h for help")
            sys.exit(0)
        else:
            
            for test in list_test_wanted:
                tests.append(dict_tests[test])

    
    suite = unittest.TestSuite()
    for test in tests:
        #suite.addTest(ParametrizedTestCase.parametrize(test, param=""))
        suite.addTest(ParametrizedTestCase.parametrize(test, param=opt_param))
    result = unittest.TextTestRunner().run(suite)

    print( "Unit tests Success "+opt_param+": ", result.wasSuccessful())
    sys.exit(not result.wasSuccessful())
