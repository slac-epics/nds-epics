/*
 * EPICS support for NDS3
 *
 * Copyright (c) 2015 Cosylab d.d.
 *
 * For more information about the license please refer to the license.txt
 * file included in the distribution.
 */

#include <iostream>
#include <fstream>
#include <link.h>
#include <set>
#include <string>
#include <sstream>

#include <epicsStdlib.h>
#include <iocshRegisterCommon.h>
#include <registryCommon.h>
#include <dbStaticPvt.h>
#include <epicsThread.h>
#include <errlog.h>
#include <epicsExit.h>

#include "nds3/exceptions.h"
#include "nds3/impl/epicsFactoryImpl.h"
#include "nds3/impl/epicsInterfaceImpl.h"
#include "nds3/impl/epicsThread.h"

// Include embedded dbd file
//#include "../dbd/dbdfile.h"

//typedef void (*reg_func)(void);
//epicsShareExtern reg_func pvar_func_arrInitialize, pvar_func_asSub,
//    pvar_func_asynInterposeEosRegister,
//    pvar_func_asynInterposeFlushRegister, pvar_func_asynRegister,
//    pvar_func_dbndInitialize, pvar_func_ndsRegister,
//    pvar_func_syncInitialize, pvar_func_tsInitialize;

namespace nds
{

const std::string EpicsFactoryImpl::getName() const
{
    return "epics";
}

static EpicsFactoryImpl* m_pFactory(0);

void EpicsFactoryImpl::createNdsDevice(const iocshArgBuf * arguments)
{
    try
    {
        if(arguments[0].sval == 0)
        {
            errlogSevPrintf(errlogInfo, "Usage of command ndsCreateDevice: ndsCreateDevice deviceName [parameters]\n");
            return;
        }
        std::string parameter;
        namedParameters_t namedParameters;
        if(arguments[1].sval != 0)
        {
            parameter = arguments[1].sval;

            for(size_t argumentNumber = 2; arguments[argumentNumber].sval != 0; ++argumentNumber)
            {
                std::string argument = arguments[argumentNumber].sval;
                size_t equalPosition = argument.find('=');
                if(equalPosition == argument.npos)
                {
                    std::ostringstream generatedName;
                    generatedName << (argumentNumber - 1);
                    namedParameters[generatedName.str()] = argument;
                }
                else
                {
                    namedParameters[argument.substr(0, equalPosition)] = argument.substr(equalPosition + 1);
                }
            }
        }

        m_pFactory->createDevice(arguments[0].sval, parameter, namedParameters);
    }
    catch(const std::exception& e)
    {
        std::ostringstream errorString;
        errorString << e.what() << std::endl;
        errlogSevPrintf(errlogInfo, "%s", errorString.str().c_str());
    }
}

void EpicsFactoryImpl::loadNdsDriver(const iocshArgBuf * arguments)
{
    try
    {
        if(arguments[0].sval == 0)
        {
            errlogSevPrintf(errlogInfo, "Usage of command ndsLoadDriver: ndsLoadDriver libraryName\n");
            return;
        }

        m_pFactory->loadDriver(arguments[0].sval);
    }
    catch(const std::runtime_error& e)
    {
        std::ostringstream errorString;
        errorString << e.what() << std::endl;
        errlogSevPrintf(errlogInfo, "%s", errorString.str().c_str());
    }
}

void EpicsFactoryImpl::loadNdsNamingRules(const iocshArgBuf * arguments)
{
    try
    {
        if(arguments[0].sval == 0)
        {
            errlogSevPrintf(errlogInfo, "Usage of command ndsLoadNamingRules: ndsLoadNamingRules iniFileName\n");
            return;
        }

        std::ifstream iniFile(arguments[0].sval);
        if ((iniFile.rdstate() & std::istream::failbit) != 0)
            throw std::runtime_error("Invalid INI file");
        m_pFactory->loadNamingRules(iniFile);
    }
    catch(const std::runtime_error& e)
    {
        std::ostringstream errorString;
        errorString << e.what() << std::endl;
        errlogSevPrintf(errlogInfo, "%s", errorString.str().c_str());
    }
}

void EpicsFactoryImpl::enableNdsNamingRules(const iocshArgBuf * arguments)
{
    try
    {
        if(arguments[0].sval == 0)
        {
            errlogSevPrintf(errlogInfo, "Usage of command ndsenableNamingRules: ndsEnableNamingRules ruleName\n");
            return;
        }

        m_pFactory->setNamingRules(arguments[0].sval);
    }
    catch(const std::runtime_error& e)
    {
        std::ostringstream errorString;
        errorString << e.what() << std::endl;
        errlogSevPrintf(errlogInfo, "%s", errorString.str().c_str());
    }
}



void EpicsFactoryImpl::ndsUserCommand(const iocshArgBuf * arguments)
{
    if(arguments[0].sval == 0 || arguments[1].sval == 0)
    {
        errlogSevPrintf(errlogInfo, "Usage of command nds: nds nodeCommand nodeName [parameters]\n");
        return;
    }

    // Retrieve the command definition
    //////////////////////////////////
    nodeCommands_t::const_iterator findCommand = m_pFactory->m_nodeCommands.find(arguments[0].sval);
    if(findCommand == m_pFactory->m_nodeCommands.end())
    {
        std::ostringstream commandsList;
        commandsList << "Command not found. Registered commands:" << std::endl;
        for(nodeCommands_t::const_iterator scanCommands(m_pFactory->m_nodeCommands.begin()), endCommands(m_pFactory->m_nodeCommands.end()); scanCommands != endCommands; ++scanCommands)
        {
            commandsList << " " << scanCommands->first << std::endl;
        }
        errlogSevPrintf(errlogInfo, "%s", commandsList.str().c_str());
        return;
    }

    // Check the node name
    //////////////////////
    std::map<std::string, command_t>::const_iterator findNode = findCommand->second.m_delegates.find(arguments[1].sval);
    if(findNode == findCommand->second.m_delegates.end())
    {
        std::ostringstream nodesList;
        nodesList << "Node not found. Registered nodes for this command:" << std::endl;
        for(std::map<std::string, command_t>::const_iterator scanNodes(findCommand->second.m_delegates.begin()), endNodes(findCommand->second.m_delegates.end());
            scanNodes != endNodes; ++scanNodes)
        {
            nodesList << " " << scanNodes->first << std::endl;
        }
        errlogSevPrintf(errlogInfo, "%s", nodesList.str().c_str());
        return;

    }

    // Check the number of parameters
    /////////////////////////////////
    parameters_t parameters;
    for(size_t argument(2); arguments[argument].sval != 0; ++argument)
    {
        parameters.push_back(arguments[argument].sval);
    }
    if(parameters.size() != findCommand->second.m_argumentsNumber)
    {
        std::ostringstream errorString;
        errorString << "Expected " << (findCommand->second.m_argumentsNumber) << " arguments but found " << parameters.size() << " instead" << std::endl;
        errlogSevPrintf(errlogInfo, "%s", errorString.str().c_str());
        return;
    }

    try
    {
        parameters_t response = findNode->second(parameters);
        for(parameters_t::const_iterator scanResponse(response.begin()), endResponse(response.end()); scanResponse != endResponse; ++scanResponse)
        {
            errlogSevPrintf(errlogInfo, "Node %s : %s", findNode->first.c_str(), scanResponse->c_str());
        }
    }
    catch(const std::runtime_error& e)
    {
        std::ostringstream errorString;
        errorString << e.what() << std::endl;
        errlogSevPrintf(errlogInfo, "%s", errorString.str().c_str());
    }

}


EpicsFactoryImpl::EpicsFactoryImpl(): m_separator("-"), m_emptyString(),m_vDbParser(0)
{
    m_pFactory = this;

    // Register the global commands
    ///////////////////////////////
    {
        commandParametersNames_t ndsLoadDriverParameters;
        ndsLoadDriverParameters.push_back("library");
        registerGlobalCommand("ndsLoadDriver", ndsLoadDriverParameters, loadNdsDriver);
    }

    {
        commandParametersNames_t ndsCreateDeviceParameters;
        ndsCreateDeviceParameters.push_back("driver");
        ndsCreateDeviceParameters.push_back("parameter");
        for(size_t createNamedParameters(0); createNamedParameters != 9; ++createNamedParameters)
        {
            std::ostringstream parameterName;
            parameterName << "namedParameter" << createNamedParameters;
            ndsCreateDeviceParameters.push_back(parameterName.str());
        }
        registerGlobalCommand("ndsCreateDevice", ndsCreateDeviceParameters, createNdsDevice);
    }

    {
        commandParametersNames_t ndsCommandParameters;
        ndsCommandParameters.push_back("commandName");
        ndsCommandParameters.push_back("nodeName");
        for(size_t createParameters(0); createParameters != 9; ++createParameters)
        {
            std::ostringstream parameterName;
            parameterName << "arg" << createParameters;
            ndsCommandParameters.push_back(parameterName.str());
        }
        registerGlobalCommand("nds", ndsCommandParameters, ndsUserCommand);
    }

    {
        commandParametersNames_t ndsLoadNamingRulesParameters;
        ndsLoadNamingRulesParameters.push_back("iniFileName");
        registerGlobalCommand("ndsLoadNamingRules", ndsLoadNamingRulesParameters, loadNdsNamingRules);
    }

    {
        commandParametersNames_t ndsEnableNamingRulesParameters;
        ndsEnableNamingRulesParameters.push_back("rulesName");
        registerGlobalCommand("ndsEnableNamingRules", ndsEnableNamingRulesParameters, enableNdsNamingRules);
    }

    initHookRegister(&EpicsFactoryImpl::epicsInitHookFunction);


}

void EpicsFactoryImpl::registerDBParser(dbParser_t dbParserFunc){
    m_vDbParser.push_back(dbParserFunc);
}


void EpicsFactoryImpl::epicsInitHookFunction(initHookState  state)
{

    if(state == initHookAfterIocRunning){
        for (size_t i =0; i<m_pFactory->m_vDbParser.size();i++)
        if(m_pFactory->m_vDbParser.at(i)!= NULL){
            m_pFactory->m_vDbParser.at(i)();
        }
    }
    /// This functionality is not used in ITER NDS v3 extension project
//    {
//        // Process all records with PINI
//        for(std::list<std::string>::const_iterator scanPVs(m_pFactory->m_processAtInit.begin()), endPVs(m_pFactory->m_processAtInit.end());
//            scanPVs != endPVs;
//            ++scanPVs)
//        {
//            std::string command("dbpf ");
//            command += *scanPVs;
//            command += ".PROC 1";
//            iocshCmd(command.c_str());
//        }
//        m_pFactory->m_processAtInit.clear();
//    }
}

InterfaceBaseImpl* EpicsFactoryImpl::getNewInterface(const std::string& fullName)
{
    return new EpicsInterfaceImpl(fullName, this);
}


void EpicsFactoryImpl::run(int argc,char * argv[])
{
/*  //TODO: Not necessary, done in st.cmd
    //iocshRegisterCommon(); //TODO: Study if necessary. Seems not as it is done in registerRecordDeviceDriver.pl

    if(argc == 0)
    {
        throw std::runtime_error("Cannot deduce the location of the DBD file");
    }

    std::string dbdFileName(argv[0]);
    size_t slashPosition = dbdFileName.rfind('/');
    if(slashPosition == std::string::npos)
    {
        dbdFileName.clear();
    }
    else
    {
        dbdFileName.erase(++slashPosition);
    }


#ifdef EPICS_SHARED_LIBRARY
    char tmpBuffer[L_tmpnam];
    std::string tmpFileName(tmpnam_r(tmpBuffer));
    std::string fileName(tmpFileName);
    std::ofstream outputStream(fileName.c_str());
    outputStream.write(dbdfile, sizeof(dbdfile));
#else
    std::string tmpFileName(dbdFileName);
    //tmpFileName += "epicsNdsControlSystem.dbd";
    tmpFileName += "ndsIoc.dbd"; //Name changed during ITER integration

#endif

    std::string command("dbLoadDatabase ");
    command += tmpFileName;
    //printf("\nEpicsFactoryImpl::run calls iocshCmd=%s\n",command.c_str());
    //iocshCmd(command.c_str());

    //iocshCmd("epicsNdsControlSystem_registerRecordDeviceDriver pdbbase");
    //iocshCmd("ndsIoc_registerRecordDeviceDriver pdbbase"); //Name changed during ITER integration
*/
    if(argc>=2) {
        iocsh(argv[1]);
        epicsThreadSleep(.2);
    }
    iocsh(0);
    epicsExit(0);

}


void EpicsFactoryImpl::registerGlobalCommand(const std::string& commandName, const commandParametersNames_t& parameters, iocshCallFunc function)
{

    iocshArgPointers_t argPointers(parameters.size());

    size_t pointersCounter(0);
    for(commandParametersNames_t::const_iterator scanParameters(parameters.begin()), endParameters(parameters.end());
        scanParameters != endParameters;
        ++scanParameters)
    {
        std::pair<keepStrings_t::const_iterator, bool> insertParameter = m_keepStrings.insert(*scanParameters);
        m_keepIocshArg.push_back(iocshArg());
        m_keepIocshArg.back().name = (*insertParameter.first).c_str();
        m_keepIocshArg.back().type = iocshArgString;
        argPointers[pointersCounter++] = &(m_keepIocshArg.back());
    }
    m_keepIocshArgPointers.push_back(argPointers);
    std::pair<keepStrings_t::const_iterator, bool> insertName = m_keepStrings.insert(commandName);

    m_keepIocshFuncDef.push_back(iocshFuncDef());
    m_keepIocshFuncDef.back().arg = m_keepIocshArgPointers.back().data();
    m_keepIocshFuncDef.back().nargs = parameters.size();
    m_keepIocshFuncDef.back().name = (*insertName.first).c_str();

    iocshRegister(&(m_keepIocshFuncDef.back()), function);


}

void EpicsFactoryImpl::processAtInit(const std::string& pvName)
{
    m_processAtInit.push_back(pvName);
}

void EpicsFactoryImpl::log(const std::string &logString, logLevel_t logLevel)
{
    switch(logLevel)
    {
    case logLevel_t::debug:
        errlogSevPrintf(errlogInfo, "%s", logString.c_str());
        break;
    case logLevel_t::info:
        errlogSevPrintf(errlogInfo, "%s", logString.c_str());
        break;
    case logLevel_t::warning:
        errlogSevPrintf(errlogMinor, "%s", logString.c_str());
        break;
    case logLevel_t::error:
        errlogSevPrintf(errlogMajor, "%s", logString.c_str());
        break;
    default:
        throw std::logic_error("Cannot log with severity level set to none");
    }
}

LogStreamGetterImpl* EpicsFactoryImpl::getLogStreamGetter()
{
    return this;
}

std::ostream* EpicsFactoryImpl::createLogStream(const logLevel_t logLevel)
{
    return new EpicsLogStream(logLevel, this);
}

void EpicsFactoryImpl::registerCommand(const BaseImpl& node,
                             const std::string& command,
                             const std::string& usage,
                             const size_t numParameters, command_t commandFunction)
{
    // Look for an already existing command
    ///////////////////////////////////////
    nodeCommands_t::iterator findCommand = m_nodeCommands.find(command);
    if(findCommand != m_nodeCommands.end())
    {
        // Check compatibility of the command definition
        if(findCommand->second.m_argumentsNumber != numParameters)
        {
            std::ostringstream errorString;
            errorString << "The number of parameters for command " << command
                        << " in the node " << node.getFullName() << " is different from the number of parameters already defined for the node "
                        << findCommand->second.m_delegates.begin()->first;

            throw std::logic_error(errorString.str());
        }
        findCommand->second.m_delegates[node.getFullName()] = commandFunction;

        // Register the command also for the external name
        if(node.getFullExternalName() != node.getFullName())
        {
            findCommand->second.m_delegates[node.getFullExternalName()] = commandFunction;
        }
        return;
    }

    std::pair<nodeCommands_t::iterator, bool> commandInsert = m_nodeCommands.insert(std::pair<std::string, nodeCommand_t>(command, nodeCommand_t()));
    commandInsert.first->second.m_commandName = command;
    commandInsert.first->second.m_usage = usage;
    commandInsert.first->second.m_argumentsNumber = numParameters;
    commandInsert.first->second.m_delegates[node.getFullName()] = commandFunction;
    // Register the command also for the external name
    if(node.getFullExternalName() != node.getFullName())
    {
        commandInsert.first->second.m_delegates[node.getFullExternalName()] = commandFunction;
    }

}

void EpicsFactoryImpl::deregisterCommand(const BaseImpl& node)
{
    std::list<std::string> eraseCommands;

    // Find the command
    ///////////////////
    for(nodeCommands_t::iterator scanCommands(m_nodeCommands.begin()), endCommands(m_nodeCommands.end());
        scanCommands != endCommands;
        ++scanCommands)
    {
        // Find the node (both full name and full external name)
        ////////////////////////////////////////////////////////
        {
            std::map<std::string, command_t>::iterator findNode = scanCommands->second.m_delegates.find(node.getFullName());
            if(findNode != scanCommands->second.m_delegates.end())
            {
                scanCommands->second.m_delegates.erase(findNode);
            }
        }

        {
            std::map<std::string, command_t>::iterator findNode = scanCommands->second.m_delegates.find(node.getFullExternalName());
            if(findNode != scanCommands->second.m_delegates.end())
            {
                scanCommands->second.m_delegates.erase(findNode);
            }
        }

        if(scanCommands->second.m_delegates.empty())
        {
            eraseCommands.push_back(scanCommands->first);
        }
    }

    // Erase the commands not bound to any node
    ///////////////////////////////////////////
    for(std::list<std::string>::const_iterator scanErase(eraseCommands.begin()), endErase(eraseCommands.end());
        scanErase != endErase;
        ++scanErase)
    {
        m_nodeCommands.erase(*scanErase);
    }
}

ThreadBaseImpl* EpicsFactoryImpl::runInThread(const std::string& name, threadFunction_t function)
{
    return new EpicsThread(this, name, function);
}

const std::string& EpicsFactoryImpl::getDefaultSeparator(const std::uint32_t nodeLevel) const
{
    if(nodeLevel == 0)
    {
        return m_emptyString;
    }
    return m_separator;
}

EpicsLogStreamBufferImpl::EpicsLogStreamBufferImpl(const logLevel_t logLevel, EpicsFactoryImpl* pEpicsFactory):
    m_logLevel(logLevel), m_pFactory(pEpicsFactory)
{
}

int EpicsLogStreamBufferImpl::sync()
{
    std::string string(std::string(pbase(), pptr() - pbase()));
    m_pFactory->log(string, m_logLevel);
    seekpos(0);
    return 0;
}

EpicsLogStream::EpicsLogStream(const logLevel_t logLevel, EpicsFactoryImpl* pEpicsFactory):
    std::ostream(&m_buffer), m_buffer(logLevel, pEpicsFactory)
{

}

}

extern "C"
{
NDS3_API nds::FactoryBaseImpl* allocateControlSystem()
{
    return new nds::EpicsFactoryImpl();
}

}
