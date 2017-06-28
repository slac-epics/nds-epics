#include <stddef.h>
#include <stdlib.h>
#include <stddef.h>
#include <string.h>
#include <stdio.h>

#include "epicsThread.h"
#include "epicsExport.h"

#include <nds3/factory.h>
#include "nds3/impl/epicsFactoryImpl.h"

static void NDSRegister(void)
{
    static int firstTime = 1;
    if (firstTime) {
        firstTime = 0;
        nds::Factory factory(std::make_shared<nds::EpicsFactoryImpl>());
        nds::Factory::registerControlSystem(factory);
    }
}

extern "C" {
    epicsExportRegistrar(NDSRegister);
}
