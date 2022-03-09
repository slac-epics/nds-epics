/*
 * EPICS support for NDS3
 *
 * Copyright (c) 2015 Cosylab d.d.
 *
 * For more information about the license please refer to the license.txt
 * file included in the distribution.
 */

#include <epicsExport.h>

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
