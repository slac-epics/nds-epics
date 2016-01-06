/*
 * EPICS support for NDS3
 *
 * Copyright (c) 2015 Cosylab d.d.
 *
 * For more information about the license please refer to the license.txt
 * file included in the distribution.
 */

#include <stddef.h>
#include <stdlib.h>
#include <stddef.h>
#include <string.h>
#include <stdio.h>

#include "epicsExit.h"
#include "epicsThread.h"
#include "iocsh.h"

#include <nds3/factory.h>
#include "../include/epicsFactoryImpl.h"

int main(int argc,char *argv[])
{
    nds::Factory factory(std::make_shared<nds::EpicsFactoryImpl>());
    nds::Factory::registerControlSystem(factory);

    factory.run(argc, argv);
    return(0);
}
