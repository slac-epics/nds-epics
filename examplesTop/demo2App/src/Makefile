TOP=../..

include $(TOP)/configure/CONFIG
#----------------------------------------
#  ADD MACRO DEFINITIONS AFTER THIS LINE
#=============================

#=============================
# Build the IOC application

PROD_IOC = demo2
# demo2.dbd will be created and installed
DBD += demo2.dbd

# demo2.dbd will be made up from these files:
demo2_DBD += base.dbd

# Include dbd files from all support applications:
demo2_DBD += asyn.dbd
demo2_DBD += nds3-epics.dbd

# Add all the support libraries needed by this IOC
demo2_LIBS += oscilloscope nds3-epics nds3 asyn

# Where to find the oscilloscope driver and enforce linking
oscilloscope_DIR += $(NDS3OSCILLOSCOPE)
demo2_LDFLAGS += -Wl,--no-as-needed

# Where to find NDS3 if it isn't installed as a system library
nds3_DIR += $(NDS3)

# demo2_registerRecordDeviceDriver.cpp derives from demo2.dbd
demo2_SRCS += demo2_registerRecordDeviceDriver.cpp

# Build the main IOC entry point on workstation OSs.
demo2_SRCS_DEFAULT += demo2Main.cpp
demo2_SRCS_vxWorks += -nil-

# Add support from base/src/vxWorks if needed
#demo2_OBJS_vxWorks += $(EPICS_BASE_BIN)/vxComLibrary

# Finally link to the EPICS Base libraries
demo2_LIBS += $(EPICS_BASE_IOC_LIBS)

#===========================

include $(TOP)/configure/RULES
#----------------------------------------
#  ADD RULES AFTER THIS LINE

