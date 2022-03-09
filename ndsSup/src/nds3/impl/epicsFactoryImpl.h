/*
 * EPICS support for NDS3
 *
 * Copyright (c) 2015 Cosylab d.d.
 *
 * For more information about the license please refer to the license.txt
 * file included in the distribution.
 */

#ifndef NDSFACTORYIMPL_CPP
#define NDSFACTORYIMPL_CPP

#include <vector>
#include <list>
#include <string>
#include <set>
#include <sstream>

#include <dbStaticLib.h>
#include <initHooks.h>
#include <registryCommon.h>
#include <iocsh.h>

#include <nds3/definitions.h>
#include <nds3/impl/factoryBaseImpl.h>
#include <nds3/impl/logStreamGetterImpl.h>

namespace nds
{

/**
 * @brief Takes care of registering everything with EPICS
 *
 */
class EpicsFactoryImpl: public FactoryBaseImpl, public LogStreamGetterImpl
{
    friend class EpicsLogStreamBufferImpl;
public:

    EpicsFactoryImpl();

    virtual const std::string getName() const;

    static void createNdsDevice(const iocshArgBuf * arguments);

    static void loadNdsDriver(const iocshArgBuf * arguments);

    static void loadNdsNamingRules(const iocshArgBuf * arguments);

    static void enableNdsNamingRules(const iocshArgBuf * arguments);

    static void ndsUserCommand(const iocshArgBuf * arguments);

    static void epicsInitHookFunction(initHookState state);

    virtual void registerDBParser(dbParser_t dbParserFunc);

    virtual InterfaceBaseImpl* getNewInterface(const std::string& fullName);

    virtual void run(int argc,char *argv[]);

    virtual LogStreamGetterImpl* getLogStreamGetter();

    virtual void registerCommand(const BaseImpl& node,
                                 const std::string& command,
                                 const std::string& usage,
                                 const size_t numParameters, command_t commandFunction);

    virtual void deregisterCommand(const BaseImpl& node);

    virtual ThreadBaseImpl* runInThread(const std::string& name, threadFunction_t function);

    virtual const std::string& getDefaultSeparator(const std::uint32_t nodeLevel) const;

    void log(const std::string& logString, logLevel_t logLevel);

    void processAtInit(const std::string& pvName);

protected:
    virtual std::ostream* createLogStream(const logLevel_t logLevel);

private:
    typedef std::list<std::string> commandParametersNames_t;
    void registerGlobalCommand(const std::string& commandName, const commandParametersNames_t& parameters, iocshCallFunc function);

    const std::string m_separator;   ///< The default separator for nodes with level 1 and higher.
    const std::string m_emptyString; ///< Default separator for nodes with level 0 (root nodes).

    typedef std::set<std::string> keepStrings_t;
    keepStrings_t m_keepStrings;                  ///< Keep the strings that need to stay around (EPICS references them).

    typedef std::list<iocshArg> keepIocshArg_t;
    keepIocshArg_t m_keepIocshArg;

    typedef std::vector<iocshArg*> iocshArgPointers_t;
    typedef std::list<iocshArgPointers_t> keepIocShArgPointers_t;
    keepIocShArgPointers_t m_keepIocshArgPointers;

    typedef std::list<iocshFuncDef> keepIocshFuncDef_t;
    keepIocshFuncDef_t m_keepIocshFuncDef;

/*
    std::vector<recordTypeLocation> m_recordTypeFunctions;
    std::list<std::string> m_recordTypeNames;
    std::vector<const char*> m_recordTypeNamesCstr;

    std::vector<dset*> m_deviceFunctions;
    std::list<std::string> m_deviceNames;
    std::vector<const char*> m_deviceNamesCstr;

    std::vector<drvet*> m_driverFunctions;
    std::list<std::string> m_driverNames;
    std::vector<const char*> m_driverNamesCstr;

    std::vector<iocshVarDef> m_variableFunctions;
    std::list<std::string> m_variableNames;
*/
    struct nodeCommand_t
    {
        nodeCommand_t(){};
        std::string m_commandName;
        std::string m_usage;
        size_t m_argumentsNumber=0;
        std::map<std::string, command_t> m_delegates;
    };
    typedef std::map<std::string, nodeCommand_t> nodeCommands_t;
    nodeCommands_t m_nodeCommands;

    std::list<std::string> m_processAtInit;
    std::vector<dbParser_t> m_vDbParser;
};

class EpicsLogStreamBufferImpl: public std::stringbuf
{
public:
    EpicsLogStreamBufferImpl(const logLevel_t logLevel, EpicsFactoryImpl* pEpicsFactory);

protected:
    virtual int sync();

    logLevel_t m_logLevel;
    EpicsFactoryImpl* m_pFactory;
};

class EpicsLogStream: public std::ostream
{
public:
    EpicsLogStream(const logLevel_t logLevel, EpicsFactoryImpl* pEpicsFactory);

protected:
    EpicsLogStreamBufferImpl m_buffer;

};


}
#endif // NDSFACTORYIMPL_CPP
