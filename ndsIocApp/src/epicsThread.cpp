/*
 * EPICS support for NDS3
 *
 * Copyright (c) 2015 Cosylab d.d.
 *
 * For more information about the license please refer to the license.txt
 * file included in the distribution.
 */

#include "nds3/impl/epicsThread.h"

namespace nds
{

EpicsThread::EpicsThread(FactoryBaseImpl *pImpl, const std::string &name, threadFunction_t function):
    ThreadBaseImpl(pImpl, name), m_function(function)
{
    m_threadStartedEventId = epicsEventCreate(epicsEventEmpty);
    if(m_threadStartedEventId == 0)
    {
        throw std::runtime_error("Cannot allocate an EPICS event");
    }

    m_threadId = epicsThreadCreate(
                name.c_str(),
                epicsThreadPriorityMedium,
                epicsThreadGetStackSize(epicsThreadStackSmall),
                EpicsThread::process,
                this);

    if(m_threadId == 0)
    {
        epicsEventDestroy(m_threadStartedEventId);
        throw std::runtime_error("Cannot allocate an EPICS thread");
    }

    epicsEventWait(m_threadStartedEventId);
}

EpicsThread::~EpicsThread()
{
    if(m_threadStartedEventId != 0)
    {
        epicsEventDestroy(m_threadStartedEventId);
    }
}

void EpicsThread::process(void *param)
{
    EpicsThread* pThread((EpicsThread*)param);

    std::lock_guard<std::mutex> lockRunning(pThread->m_running);

    epicsEventSignal(pThread->m_threadStartedEventId);

    pThread->m_function();
}

void EpicsThread::join()
{
    std::lock_guard<std::mutex> lockRunning(m_running);
}


}
