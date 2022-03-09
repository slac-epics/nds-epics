TOP=../..

include $(TOP)/configure/CONFIG
#----------------------------------------
#  ADD MACRO DEFINITIONS AFTER THIS LINE
#=============================
# Build the IOC application

PROD_IOC += ndsex1
USR_CXXFLAGS_Linux = -std=c++11 -Wextra -pedantic

# ndsex1.dbd will be created and installed
DBD += ndsex1.dbd

# ndsIoc.dbd will be made up from these files:
#USR_DBDFLAGS=-I../../../../dbd
USR_DBDFLAGS= -I$(TOP)/../dbd
ndsex1_DBD += base.dbd
ndsex1_DBD += asyn.dbd
ndsex1_DBD += nds3-epics.dbd

# Add all the support libraries needed by this IOC
#nds3-epics_DIR += ../../../../lib/linux-x86_64
nds3-epics_DIR += $(TOP)/../lib/$(T_A)
ndsex1_LIBS += $(CODAC_LIBS)
ndsex1_LIBS += nds3-epics
ndsex1_LIBS += asyn
ndsex1_SYS_LIBS_Linux += nds3
ndsex1_LIBS_WIN32 += nds3

# Enforce linking. This ii using rpath and this is not correct. If removed execution error because the library is not found
ndsex1_LDFLAGS_Linux += -Wl,-rpath=$(CURDIR)/../../../../lib/linux-x86_64


# ndsex1_registerRecordDeviceDriver.cpp derives from ndsex1.dbd
ndsex1_SRCS += ndsex1_registerRecordDeviceDriver.cpp

# Build the main IOC entry point on workstation OSs.
ndsex1_SRCS_DEFAULT += ndsex1Main.cpp
ndsex1_SRCS_vxWorks += -nil-





# Finally link to the EPICS Base libraries
ndsex1_LIBS += $(EPICS_BASE_IOC_LIBS)

#=============================

include $(TOP)/configure/RULES
#----------------------------------------
#  ADD RULES AFTER THIS LINE

