#!/usr/bin/env python
'''IOC test configuration'''

import os
import sys

# Do we want verbose logging
verbose = False

# Duration of standalong runs

iocRunDuration = 10


# Defaults for EPICS properties:

hostArch = "linux-x86_64"

iocExecutable = "softIoc"

iocDebug = 10

def setup():
    '''Sets up test parameters for CA Gateway tests
    '''
    
    global verbose, hostArch
    global iocExecutable 

    if 'VERBOSE' in os.environ and os.environ['VERBOSE'].lower().startswith('y'):
        verbose = True

    if 'EPICS_HOST_ARCH' in os.environ:
        hostArch = os.environ['EPICS_HOST_ARCH']
    elif 'T_A' in os.environ:
        hostArch = os.environ['T_A']
    else:
        print("Warning: EPICS_HOST_ARCH not set. Using default value of '{0}'".format(hostArch))
    
    iocExecutable=os.path.join(os.getcwd(),'../../examplesTop/bin', hostArch, 'ndsex1')
    #print("Path to IOC"+ iocExecutable)
   
