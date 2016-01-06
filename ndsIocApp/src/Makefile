TOP=../..

include $(TOP)/configure/CONFIG
#----------------------------------------
#  ADD MACRO DEFINITIONS AFTER THIS LINE
#=============================

#=============================
# Build the IOC application

PROD_IOC = epicsNdsControlSystem

# ndsTestLibrary.dbd will be created and installed
DBD += epicsNdsControlSystem.dbd

# ndsTestLibrary.dbd will be made up from these files:
epicsNdsControlSystem_DBD += base.dbd

# Include dbd files from all support applications:
epicsNdsControlSystem_DBD += asyn.dbd

# Add all the support libraries needed by this IOC
epicsNdsControlSystem_LIBS += asyn

#epicsNdsControlSystem_registerRecordDeviceDriver.cpp derives from epicsNdsControlSystem.dbd
epicsNdsControlSystem_SRCS += epicsNdsControlSystem_registerRecordDeviceDriver.cpp

# Build the main IOC entry point on workstation OSs.
epicsNdsControlSystem_SRCS_DEFAULT += epicsFactoryImpl.cpp epicsInterfaceImpl.cpp ndsIocApp.cpp epicsThread.cpp
epicsNdsControlSystem_SRCS_vxWorks += -nil-

USR_CPPFLAGS=-std=c++0x -Wall -Wextra -pedantic -fPIC -pthread

# Add support from base/src/vxWorks if needed
#ndsTestLibrary_OBJS_vxWorks += $(EPICS_BASE_BIN)/vxComLibrary

# Finally link to the EPICS Base libraries...
epicsNdsControlSystem_LIBS += $(EPICS_BASE_IOC_LIBS)

# ...and the other needed libs
epicsNdsControlSystem_LDFLAGS += -lrt -ldl -lpthread -lnds3

DBDINSTALL += epicsNdsControlSystem.dbd


#===========================

include $(TOP)/configure/RULES
#----------------------------------------
#  ADD RULES AFTER THIS LINE


