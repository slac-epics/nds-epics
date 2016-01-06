TEMPLATE = app
QT -= qt
#CONFIG += dll
TARGET = epicsNdsControlSystem

# Target that includes the dbd file into a cpp file
# Define how to create dbd.h
#dbd.target = dbd.h
#dbd.commands = echo \'static const char dbdfile[] = {\' > $$PWD/dbd/dbdfile.h && \
#               xxd -i < $$PWD/dbd/dbdfile.dbd >> $$PWD/dbd/dbdfile.h && \
#               echo \'};\' >> $$PWD/dbd/dbdfile.h
#dbd.depends = FORCE

#QMAKE_EXTRA_TARGETS += dbd

#PRE_TARGETDEPS += dbd.h

# Find EPICS libraries position
#------------------------------
EPICS_BASE = $$(EPICS_BASE)
EPICS_HOST_ARCH = $$(EPICS_HOST_ARCH)

LIBS_BASE = $$EPICS_BASE/lib/$$EPICS_HOST_ARCH
LIBS_ASYN = $$EPICS_BASE/../modules/asyn/lib/$$EPICS_HOST_ARCH

# Library flags
#--------------
QMAKE_CXXFLAGS += -std=c++0x -Wall -Wextra -pedantic -fPIC -pthread
QMAKE_LFLAGS += -fPIC -Wl,-as-needed

# Epics only library flags
#-------------------------
QMAKE_LFLAGS += -Wl,-rpath,$$LIBS_BASE
QMAKE_LFLAGS += -Wl,-rpath,$$LIBS_ASYN

# We are building the library, export symbols
#--------------------------------------------
DEFINES += NDS3_DLL
DEFINES += NDS3_DLL_IMPORTS

LIBS += -L$$LIBS_BASE \
    -L$$LIBS_ASYN \
    -ldbCore -ldbRecStd -lgdd -lasyn \
    -lca -lcas -lCom -ldl -lnds3

tango:LIBS += -L/usr/local/lib -ltango -llog4tango -lomniORB4 -lomnithread -lomniDynamic4

INCLUDEPATH += $$EPICS_BASE/include \
    $$EPICS_BASE/include/compiler/gcc \
    $$EPICS_BASE/include/os/Linux/ \
    $$EPICS_BASE/../modules/asyn/include \

tango:INCLUDEPATH += /usr/local/include/tango /usr/include/omniORB4



SOURCES += \
    ndsIocApp/src/epicsInterfaceImpl.cpp \
    ndsIocApp/src/epicsFactoryImpl.cpp \
    ndsIocApp/src/scansymbols.cpp \
    ndsIocApp/src/ndsIocApp.cpp \
    ndsIocApp/src/epicsThread.cpp

HEADERS += \
    ndsIocApp/include/epicsInterfaceImpl.h \
    ndsIocApp/include/epicsFactoryImpl.h \
    ndsIocApp/include/scansymbols.h \
    ndsIocApp/include/epicsThread.h

OTHER_FILES += \
    dbd/dbdfile.dbd
