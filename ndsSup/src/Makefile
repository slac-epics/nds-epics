TOP=../..

include $(TOP)/configure/CONFIG
#----------------------------------------
#  ADD MACRO DEFINITIONS AFTER THIS LINE
#=============================

USR_CPPFLAGS=-std=c++11 -Wall -Wextra -pedantic -fPIC -pthread

USR_INCLUDES += -I$(NDS3_INCLUDE)

# ======================================================
# PATH TO "NON EPICS" EXTERNAL PACKAGES: USER LIBRARIES
# ======================================================
nds3_DIR = $(NDS3_LIB)

# ======================================================
# LINK "NON EPICS" EXTERNAL PACKAGE LIBRARIES STATICALLY
#=======================================================
USR_LIBS_Linux += nds3

#======================================================
# Build an IOC support library
#======================================================
PROD_NAME = nds3epics
LIBRARY_IOC += $(PROD_NAME)

# Install dbd files
DBD += $(PROD_NAME).dbd

$(PROD_NAME)_DBD += base.dbd
$(PROD_NAME)_DBD += asyn.dbd
$(PROD_NAME)_DBD += nds3epicsSupport.dbd

INC += nds3/impl/epicsFactoryImpl.h
INC += nds3/impl/epicsInterfaceImpl.h
INC += nds3/impl/epicsThread.h

# The following are compiled and added to the support library
$(PROD_NAME)_SRCS += epicsFactoryImpl.cpp
$(PROD_NAME)_SRCS += epicsInterfaceImpl.cpp
$(PROD_NAME)_SRCS += epicsThread.cpp
$(PROD_NAME)_SRCS += ndsRegister.cpp

$(PROD_NAME)_LIBS += asyn

$(PROD_NAME)_LIBS += $(EPICS_BASE_IOC_LIBS)

#===========================

include $(TOP)/configure/RULES
#----------------------------------------
#  ADD RULES AFTER THIS LINE
