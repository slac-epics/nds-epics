/*
 * EPICS support for NDS3
 *
 * Copyright (c) 2015 Cosylab d.d.
 *
 * For more information about the license please refer to the license.txt
 * file included in the distribution.
 */

#ifndef EPICSTHREAD_H
#define EPICSTHREAD_H

#include <nds3/definitions.h>
#include <nds3impl/factoryBaseImpl.h>
#include <nds3impl/threadBaseImpl.h>
#include <epicsThread.h>
#include <mutex>

namespace nds
{

class EpicsThread: public ThreadBaseImpl
{
public:
    EpicsThread(FactoryBaseImpl* pImpl, const std::string& name, threadFunction_t function);

    ~EpicsThread();

    void join();

protected:
    static void process(void* param);

private:
    threadFunction_t m_function;
    epicsThreadId m_threadId;
    epicsEventId m_threadStartedEventId;

    std::mutex m_running;
};

}
#endif // EPICSTHREAD_H
