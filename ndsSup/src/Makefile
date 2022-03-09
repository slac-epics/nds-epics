TOP=../..

include $(TOP)/configure/CONFIG
#----------------------------------------
#  ADD MACRO DEFINITIONS AFTER THIS LINE
#=============================

#==================================================
# build a support library

LIBRARY_IOC += nds3-epics

# install nds3-epics.dbd into <top>/dbd
DBD += nds3-epics.dbd

INC += nds3/impl/epicsFactoryImpl.h
INC += nds3/impl/epicsInterfaceImpl.h
INC += nds3/impl/epicsThread.h

USR_INCLUDES_WIN32 += -I../../../nds-core/include

# Include flag -DAUTOGEN_DB if auto generated db files wanted (not tested)
USR_CXXFLAGS_Linux=-std=c++11 -Wall -Wextra -pedantic -g
USR_CXXFLAGS_WIN32=-DNOMINMAX -DAUTOGEN_DB -DNO_TCN

# specify all source files to be compiled and added to the library
nds3-epics_SRCS += epicsFactoryImpl.cpp
nds3-epics_SRCS += epicsInterfaceImpl.cpp
nds3-epics_SRCS += epicsThread.cpp
nds3-epics_SRCS += ndsRegister.cpp

# Not strictly needed, but creates useful info in the library

nds3-epics_LIBS += asyn
nds3-epics_LIBS += $(EPICS_BASE_IOC_LIBS)
nds3-epics_SYS_LIBS_Linux += nds3
nds3-epics_LIBS_WIN32 += nds3

#===========================

include $(TOP)/configure/RULES
#----------------------------------------
#  ADD RULES AFTER THIS LINE
