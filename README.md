# EPICS layer for NDS3

This project contains the EPICS layer for the NDS3 framework. It has three important directories, `ndsSup`, `demo` and `demo2`.

* `ndsSup` contains the NDS EPICS layer software library `nds3epics`.
* `demo` contains the first demonstration IOC which demostrates that drivers can be loaded at runtime before IOC init instead of being linked against. The drivers used in the demos are in the NDS3 repository.
* `demo2` contains the second demonstration IOC which is using Gnu Linker to load the driver instead.

In order to compile and use this project [NDS3](https://github.com/cosylab/nds3) *has to be* installed.

[![Build Status](https://travis-ci.org/Cosylab/nds3_epics.svg?branch=master)](https://travis-ci.org/Cosylab/nds3_epics)

## Manual Installation

### Prerequisites

* [EPICS Base](http://www.aps.anl.gov/epics/base/index.php)
* [Asyn](http://www.aps.anl.gov/epics/modules/soft/asyn/)
* [NDS3](https://github.com/cosylab/nds3)

### Build and run

- Update the configure/RELEASE file with the correct location for EPICS base, Asyn and NDS3.
- Run `make` from the project root folder.
- Run IOC with `cd iocBoot/iocdemo && ../../bin/linux-x86_64/demo st.cmd`.

More detailed instructions can be found in [run_demo.md](doc/run_demo.md).

## Usage

Example of usage:

    [root@8b8481acd71f iocdemo]# ../../bin/linux-x86_64/demo st.cmd
    #!../../bin/linux-x86_64/demo
    ## You may have to change demo to something else
    ## everywhere it appears in this file
    < envPaths
    epicsEnvSet("IOC","iocdemo")
    epicsEnvSet("TOP","/root/nds3_epics")
    epicsEnvSet("ASYN","/root/asyn4-31")
    epicsEnvSet("NDS3","/usr/lib64")
    epicsEnvSet("NDS3OSCILLOSCOPE","/usr/lib64/nds3")
    epicsEnvSet("EPICS_BASE","/root/base-3.15.5")
    ## Register all support components
    dbLoadDatabase("../../dbd/demo.dbd",0,0)
    demo_registerRecordDeviceDriver(pdbbase)
    ndsLoadDriver("/usr/lib64/nds3/liboscilloscope.so")
    ndsCreateDevice(Oscilloscope, "test1")
    iocInit()
    Starting iocInit
    ############################################################################
    ## EPICS R3.15.5
    ## EPICS Base built Jun 26 2017
    ############################################################################
    Warning: RSRV has empty beacon address list
    iocRun: All initialization complete
    DBR_UCHAR:          1         0x1
    DBR_UCHAR:          1         0x1
    DBR_UCHAR:          1         0x1
    DBR_UCHAR:          1         0x1
    DBR_UCHAR:          1         0x1
    DBR_UCHAR:          1         0x1
    epics> dbl
    test1-SinWave-StateMachine-getGlobalState
    test1-SinWave-StateMachine-getState
    test1-SquareWave-StateMachine-getGlobalState
    test1-SquareWave-StateMachine-getState
    test1-SinWave-StateMachine-setState
    test1-SquareWave-StateMachine-setState
    test1-SinWave-Duration
    test1-SinWave-Frequency
    test1-SquareWave-Duration
    test1-SquareWave-Frequency
    test1-SinWave-Data
    test1-SquareWave-Data
    test1-SinWave-decimation
    test1-SquareWave-decimation
    test1-maxSinAmplitude
    test1-maxSquareAmplitude
    epics> nds switchOn test1-SinWave
    epics> nds start test1-SinWave
