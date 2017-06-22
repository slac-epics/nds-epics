#!../../bin/linux-x86_64/demo2

## You may have to change demo2 to something else
## everywhere it appears in this file

< envPaths

## Register all support components
dbLoadDatabase("../../dbd/demo2.dbd",0,0)
demo2_registerRecordDeviceDriver(pdbbase) 

ndsCreateDevice(Oscilloscope, "test1")

iocInit()
