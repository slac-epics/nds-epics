/*
 * EPICS support for NDS3
 *
 * Copyright (c) 2015 Cosylab d.d.
 *
 * For more information about the license please refer to the license.txt
 * file included in the distribution.
 */

#ifndef NDSEPICSINTERFACEIMPL_H
#define NDSEPICSINTERFACEIMPL_H

#include <string>
#include <vector>
#include <set>

#include <asynPortDriver.h>

#include <nds3/impl/interfaceBaseImpl.h>
#include <nds3/definitions.h>
namespace nds
{

class EpicsFactoryImpl;

/**
 * @internal
 * @brief The AsynInterface class. Allocated by AsynPort
 *        to communicate with the AsynDriver
 */
class EpicsInterfaceImpl: public InterfaceBaseImpl, asynPortDriver
{
public:
    EpicsInterfaceImpl(const std::string& portName, EpicsFactoryImpl* pEpicsFactory);
    ~EpicsInterfaceImpl();
    virtual void registerPV(std::shared_ptr<PVBaseImpl> pv);

    virtual void deregisterPV(std::shared_ptr<PVBaseImpl> pv);

    virtual void registrationTerminated();

    virtual void push(const PVBaseImpl& pv, const timespec& timestamp, const std::int32_t& value, const statusPV_t& status = statusPV_t::success);
    virtual void push(const PVBaseImpl& pv, const timespec& timestamp, const std::int64_t& value, const statusPV_t& status = statusPV_t::success);
    virtual void push(const PVBaseImpl& pv, const timespec& timestamp, const float& value, const statusPV_t& status = statusPV_t::success);
    virtual void push(const PVBaseImpl& pv, const timespec& timestamp, const double& value, const statusPV_t& status = statusPV_t::success);
    virtual void push(const PVBaseImpl& pv, const timespec& timestamp, const std::vector<std::int8_t> & value, const statusPV_t& status = statusPV_t::success);
    virtual void push(const PVBaseImpl& pv, const timespec& timestamp, const std::vector<std::uint8_t> & value, const statusPV_t& status = statusPV_t::success);
    virtual void push(const PVBaseImpl& pv, const timespec& timestamp, const std::vector<std::int32_t> & value, const statusPV_t& status = statusPV_t::success);
    virtual void push(const PVBaseImpl& pv, const timespec& timestamp, const std::vector<std::int64_t> & value, const statusPV_t& status = statusPV_t::success);
    virtual void push(const PVBaseImpl& pv, const timespec& timestamp, const std::vector<float> & value, const statusPV_t& status = statusPV_t::success);
    virtual void push(const PVBaseImpl& pv, const timespec& timestamp, const std::vector<double> & value, const statusPV_t& status = statusPV_t::success);
    virtual void push(const PVBaseImpl& pv, const timespec& timestamp, const std::string& value, const statusPV_t& status = statusPV_t::success);
    virtual void push(const PVBaseImpl& pv, const timespec& timestamp, const timespec & value, const statusPV_t& status = statusPV_t::success);

    virtual void push(const PVBaseImpl& pv, const timespec& timestamp, const timestamp_t& value, const statusPV_t& status = statusPV_t::success);
    virtual void push(const PVBaseImpl& pv, const timespec& timestamp, const std::vector<timespec> & value, const statusPV_t& status = statusPV_t::success);
    virtual void push(const PVBaseImpl& pv, const timespec& timestamp, const std::vector<bool> & value, const statusPV_t& status = statusPV_t::success);
    virtual void push(const PVBaseImpl& pv, const timespec& timestamp, const std::vector<std::uint16_t> & value, const statusPV_t& status = statusPV_t::success);
    virtual void push(const PVBaseImpl& pv, const timespec& timestamp, const std::vector<std::int16_t> & value, const statusPV_t& status = statusPV_t::success);
    virtual void push(const PVBaseImpl& pv, const timespec& timestamp, const std::vector<std::uint32_t> & value, const statusPV_t& status = statusPV_t::success);

    virtual asynStatus readInt32(asynUser *pasynUser, epicsInt32 *value);
    virtual asynStatus writeInt32(asynUser *pasynUser, epicsInt32 value);

    virtual asynStatus readInt64(asynUser *pasynUser, epicsInt64 *value);
    virtual asynStatus writeInt64(asynUser *pasynUser, epicsInt64 value);

    virtual asynStatus readFloat32(asynUser *pasynUser, epicsFloat64 *value);
    virtual asynStatus writeFloat32(asynUser *pasynUser, epicsFloat64 value);

    virtual asynStatus readFloat64(asynUser *pasynUser, epicsFloat64 *value);
    virtual asynStatus writeFloat64(asynUser *pasynUser, epicsFloat64 value);

    virtual asynStatus readInt8Array(asynUser *pasynUser, epicsInt8* pValue,
                                                  size_t nElements, size_t *nIn);
    virtual asynStatus writeInt8Array(asynUser *pasynUser, epicsInt8* pValue,
                                                   size_t nElements);

    virtual asynStatus readInt16Array(asynUser *pasynUser, epicsInt16* pValue,
                                                  size_t nElements, size_t *nIn);
    virtual asynStatus writeInt16Array(asynUser *pasynUser, epicsInt16* pValue,
                                                   size_t nElements);

    virtual asynStatus readFloat32Array(asynUser *pasynUser, float* pValue,
                                                  size_t nElements, size_t *nIn);
    virtual asynStatus writeFloat32Array(asynUser *pasynUser, float* pValue,
                                                   size_t nElements);

    virtual asynStatus readInt64Array(asynUser *pasynUser, epicsInt64 *value,
                                                     size_t nElements, size_t *nIn);
    virtual asynStatus writeInt64Array(asynUser *pasynUser, epicsInt64 *value,
                                                      size_t nElements);

    virtual asynStatus readFloat64Array(asynUser *pasynUser, double* pValue,
                                                  size_t nElements, size_t *nIn);
    virtual asynStatus writeFloat64Array(asynUser *pasynUser, double* pValue,
                                                   size_t nElements);

    virtual asynStatus readInt32Array(asynUser *pasynUser, epicsInt32 *value,
                                                  size_t nElements, size_t *nIn);
    virtual asynStatus writeInt32Array(asynUser *pasynUser, epicsInt32 *value,
                                                   size_t nElements);

    virtual asynStatus drvUserCreate(asynUser *pasynUser, const char *drvInfo,
                                     const char **pptypeName, size_t *psize);

    timespec convertEpicsTimeToUnixTime(const epicsTimeStamp& time);
    epicsTimeStamp convertUnixTimeToEpicsTime(const timespec& time);
    asynStatus convertStatusPVToAsynStatus(const statusPV_t& status);


    virtual void registerReporter(reporter_t reporter);
    virtual void report(FILE* file , int details);

private:
    template<typename T, typename interruptType>
    void pushOneValue(const PVBaseImpl& pv, const timespec& timestamp, const T& value, void* interruptPvt, const statusPV_t& status = statusPV_t::success);

    template<typename T, typename interruptType>
    void pushArray(const PVBaseImpl& pv, const timespec& timestamp, const T* pValue, size_t numElements, void* interruptPvt, const statusPV_t& status = statusPV_t::success);

    template<typename T>
    asynStatus writeOneValue(asynUser* pasynUser, const T& pValue);

    template<typename T>
    asynStatus readOneValue(asynUser* pasynUser, T* pValue);


    template<typename T>
    asynStatus readArray(asynUser *pasynUser, T* pValue, size_t nElements, size_t *nIn);

    template<typename T>
    asynStatus writeArray(asynUser *pasynUser, T* pValue, size_t nElements);

    /**
     * @brief This method reads data U (NDS), and converts them to to data T (EPICS compliant)
     *        if necessary. Data conversions supported: 
     *         timespec              <--> asynInt32Array
     *         timestamp_t           <--> asynInt32Array
     *         std::vector<timespec> <--> asynInt32Array
     *         std::vector<uint32_t> <--> asynInt32Array
     *         std::vector<uint16_t> <--> asynInt16Array
     *         std::vector<bool>     <--> asynInt32Array
     *
     * @return asyn status
     * @warning  there are some not safe conversion between unsigned and signed types
     *  **/
    template<typename T, typename U>
    asynStatus readArray_NDStypes(asynUser *pasynUser, T* pValue, size_t nElements, size_t *nIn);

    /**
     * @brief This method writes data U (NDS), previous conversion from data T (EPICS compliant)
     *        if necessary. 
     * @return asyn status
     * @see  readArray_NDStypes
     * @warning  there are some not safe conversion between unsigned and signed types
     * */
    template<typename T, typename U>
    asynStatus writeArray_NDStypes(asynUser *pasynUser, T* pValue, size_t nElements);

    typedef std::pair<const char*, size_t> errorAndSize_t;

    /**
     * @brief Use this method to retrieve a static pointer to an error message to
     *        use with asynUser->errorMessage.
     *
     * The error message will stay in memory until the EpicsInterfaceImpl object is
     * deleted.
     *
     * @param error the error message
     * @return a pair containing a static pointer and the error length, in chars
     */
    errorAndSize_t getErrorString(const std::string& error);

    std::vector<std::shared_ptr<PVBaseImpl> > m_pvs;

    std::map<std::string, size_t> m_pvNameToReason;

    std::string m_autogeneratedDB;

    std::set<std::string> m_errorMessages;

    reporter_t reporter;

    EpicsFactoryImpl* m_pEpicsFactory;


};

}

#endif // NDSEPICSINTERFACEIMPL_H
