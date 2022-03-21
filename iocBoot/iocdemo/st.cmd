#!../../bin/linux-x86_64/demo

## You may have to change demo to something else
## everywhere it appears in this file

< envPaths

## Register all support components
dbLoadDatabase("../../dbd/demo.dbd",0,0)
demo_registerRecordDeviceDriver(pdbbase) 

ndsLoadDriver("${NDS3OSCILLOSCOPE}/liboscilloscope.so")
ndsCreateDevice(Oscilloscope, "test1")

iocInit()
