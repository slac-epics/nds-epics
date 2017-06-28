TOP=../..

include $(TOP)/configure/CONFIG
#----------------------------------------
#  ADD MACRO DEFINITIONS AFTER THIS LINE
#=============================

USR_CPPFLAGS=-std=c++0x -Wall -Wextra -pedantic -fPIC -pthread

#==================================================
# build a support library

LIBRARY_IOC += nds3epics

# install nds3.dbd into <top>/dbd
DBD += nds3epics.dbd

# specify all source files to be compiled and added to the library
nds3epics_SRCS += epicsFactoryImpl.cpp
nds3epics_SRCS += epicsInterfaceImpl.cpp
nds3epics_SRCS += epicsThread.cpp
nds3epics_SRCS += ndsRegister.cpp

#INC += nds3/impl/epicsFactoryImpl.h
#INC += nds3/impl/epicsInterfaceImpl.h
#INC += nds3/impl/epicsThread.h

nds3epics_LIBS += nds3
nds3_DIR = $(NDS3)

nds3epics_LIBS += $(EPICS_BASE_IOC_LIBS)

#===========================

include $(TOP)/configure/RULES
#----------------------------------------
#  ADD RULES AFTER THIS LINE

