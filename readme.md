# EPICS layer for NDS3

This project contains the EPICS layer for the NDS3 framework.

In order to compile and use this project YOU HAVE TO INSTALL NDS3 first.

The compilation produces an IOC Application that can load and execute device supports written using the NDS3 framework.
The DBD file produced by the compilation must reside in the same folder where the executable epicsNdsControlSystem is present.

## Compilation

### Solution 1

- modify the configure/RELEASE file and set the proper folders
- run make from the project root folder
- copy the dbd file from the dbd folder to the bin/{architecture} folder

Run the executable with
    ./bin/linux-x86_64/epicsNdsControlSystem

### Solution 2

- Make sure that the enviroment variables EPICS_BASE and EPICS_MODULES are set correctly
- run "ant" from the project root folder 

Ant internally executes the same steps as in the "Solution 1", taking the proper setting from the configuration
 variables. The results are copied into the folder "artifacts" (created by ant) while the build is executed
 in a temporary folder "build" (also created by ant).

Run the executable with
    ./artifacts/epicsNdsControlSystem


## Usage

Example of usage:

    $> epicsNdsControlSystem
    epics> ndsLoadDriver '/home/codac-dev/Documents/oscilloscope-build-desktop-Qt_4_6_2_Debug/liboscilloscope.so.1' 
    epics> ndsCreateDevice Oscilloscope test1
    epics> iocInit
    Starting iocInit
    ############################################################################
    ## EPICS R3.15.1 $Date: Mon 2014-12-01 15:07:38 -0600$
    ## EPICS Base built Feb 20 2015
    ############################################################################
    iocRun: All initialization complete
    epics> dbl
    test1-SinWave-Duration
    test1-SinWave-Frequency
    test1-SquareWave-Duration
    test1-SquareWave-Frequency
    test1-Output
    test1-SinWave-Data
    test1-SquareWave-Data
    test1-SinWave-StateMachine-getGlobalState
    test1-SinWave-StateMachine-getState
    test1-SquareWave-StateMachine-getGlobalState
    test1-SquareWave-StateMachine-getState
    test1-SinWave-decimation
    test1-SquareWave-decimation
    test1-maxSinAmplitude
    test1-maxSquareAmplitude
    test1-SinWave-StateMachine-setState
    test1-SquareWave-StateMachine-setState
    epics> nds switchOn test1-SinWave
    epics> nds start test1-SinWave


