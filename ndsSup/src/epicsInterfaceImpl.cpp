/*
 * EPICS support for NDS3
 *
 * Copyright (c) 2015 Cosylab d.d.
 *
 * For more information about the license please refer to the license.txt
 * file included in the distribution.
 */

/**
 * @file epicsInterfaceImpl.cpp
 *
 * Contains the implementation of the interface to the EPICS system.
 *
 */

#include <cstdint>
#include <sstream>
#include <ostream>
#include <fstream>
#include <stdexcept>
#include <memory.h>
#include <typeinfo>

#include <iocsh.h>

#ifdef _WIN32
#include <winsock2.h>
#include <ws2ipdef.h>
#endif

#include <nds3/pvBase.h>
#include <nds3/exceptions.h>
#include <nds3/definitions.h>
#include <nds3/impl/pvBaseImpl.h>
#include <nds3/impl/pvActionImpl.h>
#include <nds3/impl/pvVariableInImpl.h>
#include <nds3/impl/portImpl.h>

#include "nds3/impl/epicsInterfaceImpl.h"
#include "nds3/impl/epicsFactoryImpl.h"

#include <errlog.h>
#include <limits>
#include <iostream>

namespace nds
{
  /*
   * Constructor
   *
   *************/
  EpicsInterfaceImpl::EpicsInterfaceImpl(const std::string& portName, EpicsFactoryImpl* pEpicsFactory):
    asynPortDriver(
        portName.c_str(),
        0,    /* maxAddr */
        asynCommonMask |
        asynDrvUserMask |
        //asynOptionMask |
        asynInt32Mask |
        asynInt64Mask |
        // asynUInt32DigitalMask |
        asynFloat64Mask  |
        //asynOctetMask |
        asynInt8ArrayMask |
        asynInt16ArrayMask |
        asynInt32ArrayMask |
        asynInt64ArrayMask |
        asynFloat32ArrayMask |
        asynFloat64ArrayMask
        //asynGenericPointerMask,   /* Interface mask */
        ,
        asynInt32Mask |
        asynInt64Mask |
        // asynUInt32DigitalMask |
        asynFloat64Mask |
    //asynOctetMask |
    asynInt8ArrayMask |
    asynInt16ArrayMask |
    asynInt32ArrayMask |
    asynFloat32ArrayMask |
    asynInt64ArrayMask |
    asynFloat64ArrayMask
    //asynGenericPointerMask,            /* Interrupt mask */
    , ASYN_CANBLOCK | ASYN_MULTIDEVICE,  /* asynFlags. */
    1,                                 /* Autoconnect */
    0,                                 /* Default priority */
    0),
    reporter(NULL),
    m_pEpicsFactory(pEpicsFactory)
  {

  }
 EpicsInterfaceImpl::~EpicsInterfaceImpl(){

  }

  /*
   * Convert a data type from enum to string.
   *
   * We use a switch and not a map for the conversion so we receive warnings
   *  if we forget a conversion.
   *
   *************************************************************************/
  typedef std::pair<std::string, std::string> dataTypeAndFTVL_t;
  struct recordDataFTVL_t
  {
    recordDataFTVL_t(const std::string& recordType, const std::string& dataType, const std::string ftvl):
      m_recordType(recordType),
      m_dataType(dataType),
      m_ftvl(ftvl)
    {
    }

    std::string m_recordType;
    std::string m_dataType;
    std::string m_ftvl;
  };

  recordDataFTVL_t dataTypeToEpicsString(const PVBaseImpl& pv)
  {
    if(pv.getDataDirection() == dataDirection_t::input)
    {
      switch(pv.getDataType())
      {
        case dataType_t::dataInt32:
          if(pv.getEnumerations().empty()) {
            return recordDataFTVL_t("longin", "asynInt32", "");
          } else {
            return recordDataFTVL_t("mbbi", "asynInt32", "");
          }
        case dataType_t::dataInt64:
          return recordDataFTVL_t("int64in", "asynInt64", "");
        case dataType_t::dataFloat32:
          return recordDataFTVL_t("ai", "asynFloat64", "");
        case dataType_t::dataFloat64:
          return recordDataFTVL_t("ai", "asynFloat64", "");
        case dataType_t::dataInt8Array:
          return recordDataFTVL_t("waveform", "asynInt8ArrayIn", "CHAR");
        case dataType_t::dataUint8Array:
          return recordDataFTVL_t("waveform", "asynInt8ArrayIn", "UCHAR");
        case dataType_t::dataInt32Array:
          return recordDataFTVL_t("waveform", "asynInt32ArrayIn", "LONG");
        case dataType_t::dataInt64Array:
          return recordDataFTVL_t("waveform", "asynInt64ArrayIn", "INT64");
        case dataType_t::dataInt16Array:
          return recordDataFTVL_t("waveform", "asynInt16ArrayIn", "SHORT");
        case dataType_t::dataFloat32Array:
          return recordDataFTVL_t("waveform", "asynFloat32ArrayIn", "LONG");
        case dataType_t::dataFloat64Array:
          return recordDataFTVL_t("waveform", "asynFloat64ArrayIn", "DOUBLE");
        case dataType_t::dataString:
          return recordDataFTVL_t("waveform", "asynInt8ArrayIn", "CHAR");
          /*case dataType_t::dataBool:
            return recordDataFTVL_t("longin", "asynInt32", "");*/
        case dataType_t::dataUint16Array:
          return recordDataFTVL_t("waveform", "asynInt16ArrayIn", "SHORT");
        case dataType_t::dataUint32Array:
          return recordDataFTVL_t("waveform", "asynInt32ArrayIn", "LONG");
        case dataType_t::dataBoolArray:
          return recordDataFTVL_t("waveform", "asynInt32ArrayIn", "LONG");
        case dataType_t::dataTimespec:
          return recordDataFTVL_t("waveform", "asynInt32ArrayIn", "LONG");
        case dataType_t::dataTimespecArray:
          return recordDataFTVL_t("waveform", "asynInt32ArrayIn", "LONG");
        case dataType_t::dataTimestamp:
          return recordDataFTVL_t("waveform", "asynInt32ArrayIn", "LONG");
      }


      throw std::logic_error("Unknown data type");

    }
    else
    {
      switch(pv.getDataType())
      {
        case dataType_t::dataInt32:
          if(pv.getEnumerations().empty()) {
            return recordDataFTVL_t("longout", "asynInt32", "");
          } else { 
            return recordDataFTVL_t("mbbo", "asynInt32", "");
          }
        case dataType_t::dataInt64:
          return recordDataFTVL_t("int64out", "asynInt64", "");
        case dataType_t::dataFloat32:
          return recordDataFTVL_t("ao", "asynFloat64", "");
        case dataType_t::dataFloat64:
          return recordDataFTVL_t("ao", "asynFloat64", "");
        case dataType_t::dataInt8Array:
          return recordDataFTVL_t("waveform", "asynInt8ArrayOut", "CHAR");
        case dataType_t::dataUint8Array:
          return recordDataFTVL_t("waveform", "asynInt8ArrayOut", "UCHAR");
        case dataType_t::dataInt32Array:
          return recordDataFTVL_t("waveform", "asynInt32ArrayOut", "LONG");
        case dataType_t::dataInt64Array:
          return recordDataFTVL_t("waveform", "asynInt64ArrayOut", "INT64");
        case dataType_t::dataInt16Array:
          return recordDataFTVL_t("waveform", "asynInt16ArrayOut", "SHORT");
        case dataType_t::dataFloat32Array:
                  return recordDataFTVL_t("waveform", "asynFloat32ArrayOut", "LONG");
        case dataType_t::dataFloat64Array:
          return recordDataFTVL_t("waveform", "asynFloat64ArrayOut", "DOUBLE");
        case dataType_t::dataString:
          return recordDataFTVL_t("waveform", "asynInt8ArrayOut", "CHAR");
          /*case dataType_t::dataBool:
            return recordDataFTVL_t("longout", "asynInt32", "");*/
        case dataType_t::dataUint16Array:
          return recordDataFTVL_t("waveform", "asynInt16ArrayOut", "SHORT");
        case dataType_t::dataUint32Array:
          return recordDataFTVL_t("waveform", "asynInt32ArrayOut", "LONG");
        case dataType_t::dataBoolArray:
          return recordDataFTVL_t("waveform", "asynInt32ArrayOut", "LONG");
        case dataType_t::dataTimespec:
          return recordDataFTVL_t("waveform", "asynInt32ArrayOut", "LONG");
        case dataType_t::dataTimespecArray:
          return recordDataFTVL_t("waveform", "asynInt32ArrayOut", "LONG");
        case dataType_t::dataTimestamp:
          return recordDataFTVL_t("waveform", "asynInt32ArrayOut", "LONG");

      }
      throw std::logic_error("Unknown data type");

    }
  }


  /*
   * Register a PV and generated the db file
   *
   *****************************************/
  void EpicsInterfaceImpl::registerPV(std::shared_ptr<PVBaseImpl> pv)
  {
    // Save the PV in a list. The order in the is used as "reason".
    ///////////////////////////////////////////////////////////////
    m_pvs.push_back(pv);
    m_pvNameToReason[pv->getFullNameFromPort()] = m_pvs.size() - 1;

#ifdef AUTOGEN_DB
    //ITER NDS3 extension project is not using AUTOGEN_DB (TODO). There is no test of this functionality.

    // Auto generate a db file
    //////////////////////////////////////////////////////////////////////////
    recordDataFTVL_t recordDataFTVL = dataTypeToEpicsString(*(pv.get()));

    int portAddress(0);
    std::ostringstream dbEntry;

    std::string externalName(pv->getFullExternalName());

    std::ostringstream scanType;

    switch(pv->getScanType())
    {
      case scanType_t::passive:
        scanType << "Passive";
        break;
      case scanType_t::periodic:
        scanType << pv->getScanPeriodSeconds() << " second";
        break;
      case scanType_t::interrupt:
        scanType << "I/O Intr";
        break;
    }

    dbEntry << "record(" << recordDataFTVL.m_recordType << ", \"" << externalName << "\") {" << std::endl;
    dbEntry << "    field(DESC, \"" << pv->getDescription() << "\")" << std::endl;
    dbEntry << "    field(DTYP, \"" << recordDataFTVL.m_dataType << "\")" << std::endl;

    if(!recordDataFTVL.m_ftvl.empty())
    {
      dbEntry << "    field(FTVL, \"" << recordDataFTVL.m_ftvl << "\")" << std::endl;
    }

    size_t maxElements(pv->getMaxElements());
    if(maxElements > 1)
    {
      dbEntry << "    field(NELM, " << maxElements << ")" << std::endl;
    }

    dbEntry << "    field(SCAN, \"" << scanType.str() << "\")" << std::endl;

    if(pv->getProcessAtInit())
    {
      m_pEpicsFactory->processAtInit(externalName);
      dbEntry << "    field(PINI, 1)" << std::endl;
    }

    // Add INP/OUT fields
    if(pv->getDataDirection() == dataDirection_t::input || recordDataFTVL.m_recordType == "waveform")
    {
      dbEntry << "    field(INP, \"@asyn(" << pv->getPort()->getFullName() << ", " << portAddress<< ")" << pv->getFullNameFromPort() << "\")" << std::endl;
    }
    else
    {
      dbEntry << "    field(OUT, \"@asyn(" << pv->getPort()->getFullName() << ", " << portAddress<< ")" << pv->getFullNameFromPort() << "\")" << std::endl;
    }

    // Add enumerations
    static const char* epicsEnumNames[] = {"ZR", "ON", "TW", "TH", "FR", "FV", "SX", "SV", "EI", "NI", "TE", "EL", "TV", "TT", "FT", "FF"};
    const enumerationStrings_t& enumerations = pv->getEnumerations();
    size_t enumNumber(0);
    for(enumerationStrings_t::const_iterator scanStrings(enumerations.begin()), endScan(enumerations.end()); scanStrings != endScan; ++scanStrings)
    {
      dbEntry << "    field(" << epicsEnumNames[enumNumber] << "VL, " << enumNumber << ")" << std::endl;
      dbEntry << "    field(" << epicsEnumNames[enumNumber] << "ST, \"" << *scanStrings << "\")" << std::endl;
      enumNumber++;
    }

    dbEntry << "}" << std::endl << std::endl;
    dbEntry.flush();


    PVActionImpl* actionPV = dynamic_cast<PVActionImpl*>(pv.get());
    if(actionPV)
    {
      std::ostringstream feedbackName;
      std::ostringstream feedbackExternalName;
      std::ostringstream calculationExternalName;

      feedbackName << pv->getComponentName() << "_r";
      feedbackExternalName << externalName << "_r";
      calculationExternalName << externalName << "_c";

      //Add feedback pv
      PVVariableInImpl<std::int32_t>* feedback = new PVVariableInImpl<std::int32_t>(feedbackName.str());
      std::shared_ptr<PVVariableInImpl<std::int32_t>> fb(feedback);
      fb->setScanType(scanType_t::interrupt, 0.1);
      fb->setDescription("Feedback for " + externalName);
      fb->setParent(pv->getParent(),pv->getNodeLevel());
      fb->initialize(*m_pEpicsFactory);

      actionPV->setAcknowledgePV(feedback);

      //Add FLNK field for feedback record
      dbEntry << "record(longin, \"" << feedbackExternalName.str() << "\") {" << std::endl;
      dbEntry << "    field(FLNK, \"" << calculationExternalName.str() << "\")" << std::endl;
      dbEntry << "}" << std::endl << std::endl;

      //Build calcout record
      dbEntry << "record(calcout, \"" << calculationExternalName.str() << "\") {" << std::endl;
      dbEntry << "    field(DESC, \"Calculation for" << externalName << "\")" << std::endl;
      dbEntry << "    field(SCAN, \"Passive\")" << std::endl;
      dbEntry << "    field(INPA, \"" << feedbackExternalName.str() << "\")" << std::endl;
      dbEntry << "    field(CALC, \"A\")" << std::endl;
      dbEntry << "    field(OOPT, \"Every Time\")" << std::endl;
      dbEntry << "    field(OUT, \"" << externalName << "\")" << std::endl;
      dbEntry << "}" << std::endl << std::endl;

      dbEntry.flush();
    }

    m_autogeneratedDB += dbEntry.str();
#endif
  }

  void EpicsInterfaceImpl::deregisterPV(std::shared_ptr<PVBaseImpl> /*pv*/)
  {
    // TODO
  }


  /*
   * Called after the registration of the PVs has been performed
   *
   *************************************************************/
  void EpicsInterfaceImpl::registrationTerminated()
  {
#ifdef AUTOGEN_DB
    char tmpBuffer[L_tmpnam];

    std::string tmpFileName(tmpnam(tmpBuffer));

#ifdef _WIN32
    size_t Pos;
    while ((Pos = tmpFileName.find('\\')) != std::string::npos)
        tmpFileName.replace(Pos, 1, 1, '/');
#endif // _WIN32

    std::string fileName(tmpFileName);
    std::ofstream outputStream(fileName.c_str());
    outputStream << m_autogeneratedDB;
    outputStream.flush();

    std::string command("dbLoadDatabase ");
    command += tmpFileName;
    printf("\nEpicsInterfaceImpl::registrationTerminated() calls iocshCmd=%s DISABLED\n",command.c_str());
    //printf("\nEpicsInterfaceImpl::registrationTerminated() calls iocshCmd=%s\n",command.c_str());
    //iocshCmd(command.c_str());
#endif 
  }


  void EpicsInterfaceImpl::push(const PVBaseImpl& pv, const timespec& timestamp, const std::int32_t& value, const statusPV_t& status)
  {
    pushOneValue<epicsInt32, asynInt32Interrupt>(pv, timestamp, (epicsInt32)value, asynStdInterfaces.int32InterruptPvt, status);
  }
  void EpicsInterfaceImpl::push(const PVBaseImpl& pv, const timespec& timestamp, const std::int64_t& value, const statusPV_t& status)
  {
    pushOneValue<epicsInt64, asynInt64Interrupt>(pv, timestamp, (epicsInt64)value, asynStdInterfaces.int64InterruptPvt, status);
  }
  void EpicsInterfaceImpl::push(const PVBaseImpl& pv, const timespec& timestamp, const float& value, const statusPV_t& status)
  {
    //Calling asynFloat64 interface because asynFloat32 is not defined
    pushOneValue<epicsFloat64, asynFloat64Interrupt>(pv, timestamp, (epicsFloat64)value, asynStdInterfaces.float64InterruptPvt, status);
  }

  void EpicsInterfaceImpl::push(const PVBaseImpl& pv, const timespec& timestamp, const double& value, const statusPV_t& status)
  {
    pushOneValue<epicsFloat64, asynFloat64Interrupt>(pv, timestamp, (epicsFloat64)value, asynStdInterfaces.float64InterruptPvt, status);
  }

  void EpicsInterfaceImpl::push(const PVBaseImpl& pv, const timespec& timestamp, const std::vector<std::int32_t> & value, const statusPV_t& status)
  {
    pushArray<epicsInt32, asynInt32ArrayInterrupt>(pv, timestamp, (epicsInt32*)value.data(), value.size(), asynStdInterfaces.int32ArrayInterruptPvt, status);
  }
  void EpicsInterfaceImpl::push(const PVBaseImpl& pv, const timespec& timestamp, const std::vector<std::int64_t> & value, const statusPV_t& status)
  {
    pushArray<epicsInt64, asynInt64ArrayInterrupt>(pv, timestamp, (epicsInt64*)value.data(), value.size(), asynStdInterfaces.int64ArrayInterruptPvt, status);
  }
  void EpicsInterfaceImpl::push(const PVBaseImpl& pv, const timespec& timestamp, const std::vector<float> & value, const statusPV_t& status)
  {
    pushArray<epicsFloat32, asynFloat32ArrayInterrupt>(pv, timestamp, (epicsFloat32*)value.data(), value.size(), asynStdInterfaces.float32ArrayInterruptPvt, status);
  }

  void EpicsInterfaceImpl::push(const PVBaseImpl& pv, const timespec& timestamp, const std::vector<double> & value, const statusPV_t& status)
  {
    pushArray<epicsFloat64, asynFloat64ArrayInterrupt>(pv, timestamp, (epicsFloat64*)value.data(), value.size(), asynStdInterfaces.float64ArrayInterruptPvt, status);
  }

  void EpicsInterfaceImpl::push(const PVBaseImpl& pv, const timespec& timestamp, const std::string& value, const statusPV_t& status)
  {
    pushArray<epicsInt8, asynInt8ArrayInterrupt>(pv, timestamp, (epicsInt8*)value.data(), value.size(), asynStdInterfaces.int8ArrayInterruptPvt, status);
  }

  void EpicsInterfaceImpl::push(const PVBaseImpl& pv, const timespec& timestamp, const std::vector<std::int8_t> & value, const statusPV_t& status)
  {
    pushArray<epicsInt8, asynInt8ArrayInterrupt>(pv, timestamp, (epicsInt8*)value.data(), value.size(), asynStdInterfaces.int8ArrayInterruptPvt, status);
  }

  void EpicsInterfaceImpl::push(const PVBaseImpl& pv, const timespec& timestamp, const std::vector<std::uint8_t> & value, const statusPV_t& status)
  {
    pushArray<epicsInt8, asynInt8ArrayInterrupt>(pv, timestamp, (epicsInt8*)value.data(), value.size(), asynStdInterfaces.int8ArrayInterruptPvt, status);
  }

  void EpicsInterfaceImpl::push(const PVBaseImpl& pv, const timespec& timestamp, const timespec& value, const statusPV_t& status)
  {
      std::vector<std::int32_t> ivector(2);
      ivector[0] = (std::int32_t)value.tv_sec;
      ivector[1] = (std::int32_t)value.tv_nsec;
      pushArray<epicsInt32, asynInt32ArrayInterrupt>(pv, timestamp,
              (epicsInt32*)ivector.data(), ivector.size(),
              asynStdInterfaces.int32ArrayInterruptPvt,
              status);
  }

  void EpicsInterfaceImpl::push(const PVBaseImpl& pv, const timespec& timestamp, const timestamp_t& value, const statusPV_t& status)
  {
      std::vector<std::int32_t> ivector(4);
      ivector[0] = (std::int32_t)value.timestamp.tv_sec;
      ivector[1] = (std::int32_t)value.timestamp.tv_nsec;
      ivector[2] = (std::int32_t)value.id;
      ivector[3] = (std::int32_t)value.edge;
      pushArray<epicsInt32, asynInt32ArrayInterrupt>(pv, timestamp,
              (epicsInt32*)ivector.data(), ivector.size(),
              asynStdInterfaces.int32ArrayInterruptPvt,
              status);
  }



  void EpicsInterfaceImpl::push(const PVBaseImpl& pv, const timespec& timestamp, const std::vector<timespec>& value, const statusPV_t& status)
  {
      std::vector<std::int32_t> ivector(value.size()*2);
      for (size_t i = 0; i < value.size(); i++) {
          ivector[2*i] = (std::int32_t)value[i].tv_sec;
          ivector[2*i + 1] = (std::int32_t)value[i].tv_nsec;
      }
      pushArray<epicsInt32, asynInt32ArrayInterrupt>(pv, timestamp,
              (epicsInt32*)ivector.data(), ivector.size(),
              asynStdInterfaces.int32ArrayInterruptPvt,
              status);
  }

  void EpicsInterfaceImpl::push(const PVBaseImpl& pv, const timespec& timestamp, const std::vector<bool> & value, const statusPV_t& status)
  {
    std::vector<std::int32_t> ivector(value.size());
    for (unsigned int x=0;x<value.size();x++) ivector[x]=value[x];
    pushArray<epicsInt32, asynInt32ArrayInterrupt>(pv, timestamp, (epicsInt32*)ivector.data(), ivector.size(), asynStdInterfaces.int32ArrayInterruptPvt, status);
  }

  void EpicsInterfaceImpl::push(const PVBaseImpl& pv, const timespec& timestamp, const std::vector<std::uint16_t> & value, const statusPV_t& status)
  {
    pushArray<epicsInt16, asynInt16ArrayInterrupt>(pv, timestamp, (epicsInt16*)value.data(), value.size(), asynStdInterfaces.int16ArrayInterruptPvt, status);
  }
  void EpicsInterfaceImpl::push(const PVBaseImpl& pv, const timespec& timestamp, const std::vector<std::int16_t> & value, const statusPV_t& status)
  {
    pushArray<epicsInt16, asynInt16ArrayInterrupt>(pv, timestamp, (epicsInt16*)value.data(), value.size(), asynStdInterfaces.int16ArrayInterruptPvt, status);
  }
  void EpicsInterfaceImpl::push(const PVBaseImpl& pv, const timespec& timestamp, const std::vector<std::uint32_t> & value, const statusPV_t& status)
  {
    pushArray<epicsInt32, asynInt32ArrayInterrupt>(pv, timestamp, (epicsInt32*)value.data(), value.size(), asynStdInterfaces.int32ArrayInterruptPvt, status);
  }/*
    * Push a scalar value to EPICS
    *
    ******************************/
  template<typename T, typename interruptType>
    void EpicsInterfaceImpl::pushOneValue(const PVBaseImpl& pv, const timespec& timestamp, const T& value, void* interruptPvt, const statusPV_t& status)
    {
      int reason = m_pvNameToReason[pv.getFullNameFromPort()];

      ELLLIST       *pclientList;
      int            addr;
      pasynManager->interruptStart(interruptPvt, &pclientList);
      interruptNode* pnode = (interruptNode *)ellFirst(pclientList);
      while (pnode)
      {
        interruptType *pInterrupt = (interruptType *)pnode->drvPvt;
        pasynManager->getAddr(pInterrupt->pasynUser, &addr);
        if ((pInterrupt->pasynUser->reason == reason) && (0 == addr))
        {
          pInterrupt->pasynUser->auxStatus = convertStatusPVToAsynStatus(status);
          pInterrupt->pasynUser->timestamp = convertUnixTimeToEpicsTime(timestamp);
          pInterrupt->callback(pInterrupt->userPvt, pInterrupt->pasynUser, value);

        }
        pnode = (interruptNode *)ellNext(&pnode->node);
      }
      pasynManager->interruptEnd(interruptPvt);
    }


  /*
   * Push an array to EPICS
   *
   ************************/
  template<typename T, typename interruptType>
    void EpicsInterfaceImpl::pushArray(const PVBaseImpl& pv, const timespec& timestamp, const T* pValue, size_t numElements, void* interruptPvt, const statusPV_t& status)
    {
      int reason = m_pvNameToReason[pv.getFullNameFromPort()];

      ELLLIST       *pclientList;
      int            addr;
      pasynManager->interruptStart(interruptPvt, &pclientList);

      interruptNode* pnode = (interruptNode *)ellFirst(pclientList);
      while (pnode)
      {
        interruptType *pInterrupt = (interruptType *)pnode->drvPvt; // TODO: remember the last used pointer
        pasynManager->getAddr(pInterrupt->pasynUser, &addr);
        if ((pInterrupt->pasynUser->reason == reason) && (0 == addr))
        {
          pInterrupt->pasynUser->auxStatus = convertStatusPVToAsynStatus(status);;
          pInterrupt->pasynUser->timestamp = convertUnixTimeToEpicsTime(timestamp);
          pInterrupt->callback(pInterrupt->userPvt, pInterrupt->pasynUser, (T*)pValue, numElements);

        }
        pnode = (interruptNode *)ellNext(&pnode->node);
      }
      pasynManager->interruptEnd(interruptPvt);
    }

  /*
   * Called to write one scalar value into a PV
   *
   ********************************************/
  template<typename T>
    asynStatus EpicsInterfaceImpl::writeOneValue(asynUser* pasynUser, const T& value)
    {
      epicsTimeStamp pTimeStamp;
      pasynManager->updateTimeStamp(pasynUser);
      pasynManager->getTimeStamp(pasynUser,&pTimeStamp);
      timespec timestamp = convertEpicsTimeToUnixTime(pTimeStamp);
      try
      {
          //This is required because asynDriver doesn't support Float32 variables, and will retrieve a double value...
          if(m_pvs[pasynUser->reason]->getDataType()==nds::dataType_t::dataFloat32){
              m_pvs[pasynUser->reason]->write(timestamp, (float)value);
          }else{
              m_pvs[pasynUser->reason]->write(timestamp, value);
          }
          pasynUser->timestamp = convertUnixTimeToEpicsTime(timestamp);
          pasynManager->updateTimeStamp(pasynUser);
          pasynUser->auxStatus = asynSuccess;
      }
      catch(std::runtime_error& e)
      {
          nds::NdsError *error_nds = dynamic_cast<nds::NdsError*>(&e);
                if (error_nds == NULL) {
                    pasynUser->auxStatus = asynError;
                } else {
                    switch (error_nds->status) {
                    case statusPV_t::success:
                        pasynUser->auxStatus = asynSuccess;
                        break;
                    case statusPV_t::timeout:
                        pasynUser->auxStatus = asynTimeout;
                        break;
                    case statusPV_t::overflow:
                        pasynUser->auxStatus = asynOverflow;
                        break;
                    case statusPV_t::disconnected:
                        pasynUser->auxStatus = asynDisconnected;
                        break;
                    case statusPV_t::disabled:
                        pasynUser->auxStatus = asynDisabled;
                        break;
                    case statusPV_t::error:
                        pasynUser->auxStatus = asynError;
                        break;
                    default:
                        pasynUser->auxStatus = asynError;
                    }
                }
            errorAndSize_t errorAndSize = getErrorString(e.what());
            pasynUser->errorMessage = (char*) errorAndSize.first;
            pasynUser->errorMessageSize = errorAndSize.second;
      }

      return (asynStatus)pasynUser->auxStatus;
    }


  /*
   * Called to read a scalar value from a PV
   *
   *****************************************/
  template<typename T>
    asynStatus EpicsInterfaceImpl::readOneValue(asynUser* pasynUser, T* pValue)
    {
      try
      {
        timespec timestamp = convertEpicsTimeToUnixTime(pasynUser->timestamp);
        m_pvs[pasynUser->reason]->read(&timestamp, pValue);
        pasynUser->timestamp = convertUnixTimeToEpicsTime(timestamp);
        pasynUser->auxStatus = asynSuccess;
      }
      catch(std::runtime_error& e)
      {
          nds::NdsError *error_nds = dynamic_cast<nds::NdsError*>(&e);
                        if (error_nds == NULL) {
                            pasynUser->auxStatus = asynError;
                        } else {
                            switch (error_nds->status) {
                            case statusPV_t::success:
                                pasynUser->auxStatus = asynSuccess;
                                break;
                            case statusPV_t::timeout:
                                pasynUser->auxStatus = asynTimeout;
                                break;
                            case statusPV_t::overflow:
                                pasynUser->auxStatus = asynOverflow;
                                break;
                            case statusPV_t::disconnected:
                                pasynUser->auxStatus = asynDisconnected;
                                break;
                            case statusPV_t::disabled:
                                pasynUser->auxStatus = asynDisabled;
                                break;
                            case statusPV_t::error:
                                pasynUser->auxStatus = asynError;
                                break;
                            default:
                                pasynUser->auxStatus = asynError;
                            }
                        }
                    errorAndSize_t errorAndSize = getErrorString(e.what());
                    pasynUser->errorMessage = (char*) errorAndSize.first;
                    pasynUser->errorMessageSize = errorAndSize.second;
      }

      return (asynStatus)pasynUser->auxStatus;

    }

  /*
   * Called to read an array from a PV
   *
   ***********************************/
  template <typename T, typename U> 
    asynStatus  EpicsInterfaceImpl::readArray_NDStypes(asynUser *pasynUser, 
        T* pValue, size_t nElements, size_t *nIn) {
      timespec timestamp = convertEpicsTimeToUnixTime(pasynUser->timestamp);
      std::vector<U> vec(nElements);
      m_pvs[pasynUser->reason]->read(&timestamp, &vec);
      if(vec.size() > nElements) {
        vec.resize(nElements);
      }
      *nIn = vec.size();
      if (typeid(T) != typeid(U)) {
        for (size_t i = 0; i < vec.size(); i++) {
          if ((std::int64_t)vec[i] > (std::int64_t)std::numeric_limits<T>::max()) {
            std::stringstream overflowedValue;
            std::stringstream maxValue;
            overflowedValue << vec[i];
            maxValue << std::numeric_limits<T>::max();
            errlogSevPrintf(errlogInfo, 
                "WARNING:: (%s): PV %s, contains values (%s) that are too "
                "large to be supported in EPICS, (max_value = %s)",
                __func__,
                (m_pvs[pasynUser->reason]->getFullNameFromPort()).c_str(), 
                overflowedValue.str().c_str(), maxValue.str().c_str()); 
          }
          pValue[i] = (T)vec[i];
        }  
      } else {
        for (size_t i = 0; i < vec.size(); i++) {
          pValue[i] = (T)vec[i];
        }  
      }
      pasynUser->timestamp = convertUnixTimeToEpicsTime(timestamp);
      pasynUser->auxStatus = asynSuccess;
      return (asynStatus)pasynUser->auxStatus;
    }

  
  template <>
    asynStatus EpicsInterfaceImpl::readArray_NDStypes <std::int32_t, timespec>(asynUser *pasynUser, 
        std::int32_t* pValue, size_t nElements, size_t *nIn) {
      timespec timestamp = convertEpicsTimeToUnixTime(pasynUser->timestamp);
      timespec timeNDS; 
      m_pvs[pasynUser->reason]->read(&timestamp, &timeNDS);
      if (nElements != 2 ) {
            errlogSevPrintf(errlogInfo, 
                "WARNING:: (%s): PV %s expects the number of elements to be 2\n",
                __func__, 
                (m_pvs[pasynUser->reason]->getFullNameFromPort()).c_str()); 
      }
      pValue[0] = (std::int32_t)timeNDS.tv_sec; 
      pValue[1] = (std::int32_t)timeNDS.tv_nsec;
      if (pValue[0] < 0  || pValue[1] < 0) {
        errlogSevPrintf(errlogInfo, 
            "WARNING:: (%s): PV %s, contains values that are too large"
            " to be supported in EPICS, (max_value = %d)",
            __func__,
            (m_pvs[pasynUser->reason]->getFullNameFromPort()).c_str(),
            std::numeric_limits<std::int32_t>::max());
      }

      *nIn = 2; 
      pasynUser->timestamp = convertUnixTimeToEpicsTime(timestamp);
      pasynUser->auxStatus = asynSuccess;
      return (asynStatus)pasynUser->auxStatus;
    }

  template <>
    asynStatus EpicsInterfaceImpl::readArray_NDStypes <std::int32_t, nds::timestamp_t>
                  (asynUser *pasynUser,std::int32_t* pValue, 
                   size_t nElements, size_t *nIn) {
      timespec timestamp = convertEpicsTimeToUnixTime(pasynUser->timestamp);
      nds::timestamp_t timestampNDS; 
      if (nElements != 4 ) {
            errlogSevPrintf(errlogInfo, 
                "WARNING:: (%s): PV %s expects the number of elements to be 4\n",
                __func__,
                (m_pvs[pasynUser->reason]->getFullNameFromPort()).c_str()); 
      }
      m_pvs[pasynUser->reason]->read(&timestamp, &timestampNDS);
      pValue[0] = (std::int32_t)timestampNDS.timestamp.tv_sec; 
      pValue[1] = (std::int32_t)timestampNDS.timestamp.tv_nsec;
      pValue[2] = (std::int32_t)timestampNDS.id;
      pValue[3] = (std::int32_t)timestampNDS.edge;
      if (pValue[0] < 0  || pValue[1] < 0) {
        errlogSevPrintf(errlogInfo, 
            "WARNING:: (%s): PV %s, contains values that are too large"
            " to be supported in EPICS, (max_value = %d)",
            __func__,
            (m_pvs[pasynUser->reason]->getFullNameFromPort()).c_str(),
            std::numeric_limits<std::int32_t>::max());
      }
      *nIn = 4; 
      pasynUser->timestamp = convertUnixTimeToEpicsTime(timestamp);
      pasynUser->auxStatus = asynSuccess;
      return (asynStatus)pasynUser->auxStatus;
    }

  template <>
    asynStatus EpicsInterfaceImpl::readArray_NDStypes <std::int32_t, std::vector<timespec>>(asynUser *pasynUser, 
        std::int32_t* pValue, size_t nElements, size_t *nIn) {
      timespec timestamp = convertEpicsTimeToUnixTime(pasynUser->timestamp);
      std::vector<timespec> vec_timeNDS(nElements); 
      m_pvs[pasynUser->reason]->read(&timestamp, &vec_timeNDS);
      if(vec_timeNDS.size() > nElements) {
        vec_timeNDS.resize(nElements);
      }
      *nIn = 2*vec_timeNDS.size();
      for (size_t i = 0; i < vec_timeNDS.size(); i++){
        pValue[2*i] = vec_timeNDS[i].tv_sec;
        pValue[2*i+1] = vec_timeNDS[i].tv_nsec;
        if (pValue[2*i] < 0  || pValue[2*i + 1] < 0) {
          errlogSevPrintf(errlogInfo, 
            "WARNING:: (%s): PV %s, contains values that are too large"
            " to be supported in EPICS, (max_value = %d)",
            __func__,
            (m_pvs[pasynUser->reason]->getFullNameFromPort()).c_str(),
            std::numeric_limits<std::int32_t>::max());
        }
      }

      pasynUser->timestamp = convertUnixTimeToEpicsTime(timestamp);
      pasynUser->auxStatus = asynSuccess;
      return (asynStatus)pasynUser->auxStatus;
    }

  template<typename T>
    asynStatus EpicsInterfaceImpl::readArray(asynUser *pasynUser, T* pValue, size_t nElements, size_t *nIn)
    {
      try
      {

        nds::dataType_t thisDataType = m_pvs[pasynUser->reason]->getDataType();
        switch(thisDataType) {
          case dataType_t::dataUint32Array:
            return readArray_NDStypes<T, std::uint32_t> (pasynUser, pValue, nElements, nIn);
          case dataType_t::dataUint16Array:
            return readArray_NDStypes<T, std::uint16_t> (pasynUser, pValue, nElements, nIn);
          case dataType_t::dataTimespec:
            return readArray_NDStypes<std::int32_t, timespec> (pasynUser,
                     (std::int32_t*) pValue, nElements, nIn);
          case dataType_t::dataTimestamp: 
            return readArray_NDStypes<std::int32_t, nds::timestamp_t> (pasynUser,
                      (std::int32_t*) pValue, nElements, nIn);
          case dataType_t::dataTimespecArray:
            return readArray_NDStypes<std::int32_t, std::vector<timespec>> (pasynUser,
                      (std::int32_t*) pValue, nElements, nIn);
          case dataType_t::dataBoolArray:
            return readArray_NDStypes<T, bool>(pasynUser, pValue, nElements, nIn);
          default:
            return readArray_NDStypes<T, T>(pasynUser, pValue, nElements, nIn);
        }
      }
      catch (std::runtime_error& e)
      {
          nds::NdsError *error_nds = dynamic_cast<nds::NdsError*>(&e);
                        if (error_nds == NULL) {
                            pasynUser->auxStatus = asynError;
                        } else {
                            switch (error_nds->status) {
                            case statusPV_t::success:
                                pasynUser->auxStatus = asynSuccess;
                                break;
                            case statusPV_t::timeout:
                                pasynUser->auxStatus = asynTimeout;
                                break;
                            case statusPV_t::overflow:
                                pasynUser->auxStatus = asynOverflow;
                                break;
                            case statusPV_t::disconnected:
                                pasynUser->auxStatus = asynDisconnected;
                                break;
                            case statusPV_t::disabled:
                                pasynUser->auxStatus = asynDisabled;
                                break;
                            case statusPV_t::error:
                                pasynUser->auxStatus = asynError;
                                break;
                            default:
                                pasynUser->auxStatus = asynError;
                            }
                        }
                    errorAndSize_t errorAndSize = getErrorString(e.what());
                    pasynUser->errorMessage = (char*) errorAndSize.first;
                    pasynUser->errorMessageSize = errorAndSize.second;
      }
      return asynError;
      //throw std::logic_error("Array Data could not be read");
    }

  template <typename T, typename U> 
    asynStatus EpicsInterfaceImpl::writeArray_NDStypes(asynUser *pasynUser, T* pValue, 
        size_t nElements) {
      epicsTimeStamp pTimeStamp;
      pasynManager->updateTimeStamp(pasynUser);
      pasynManager->getTimeStamp(pasynUser,&pTimeStamp);
      timespec timestamp = convertEpicsTimeToUnixTime(pTimeStamp);

      std::vector<U> vec(nElements);
      for (size_t i = 0 ; i < vec.size(); i++) {
         vec[i] = (U)pValue[i];
      }
      m_pvs[pasynUser->reason]->write(timestamp, vec);
      pasynUser->timestamp = convertUnixTimeToEpicsTime(timestamp);
      pasynUser->auxStatus = asynSuccess;
      return (asynStatus)pasynUser->auxStatus;
    }

  template <>
    asynStatus EpicsInterfaceImpl::writeArray_NDStypes<std::int32_t, timespec>
        (asynUser *pasynUser, std::int32_t* pValue, size_t /*nElements*/) {
      epicsTimeStamp pTimeStamp;
      pasynManager->updateTimeStamp(pasynUser);
      pasynManager->getTimeStamp(pasynUser,&pTimeStamp);
      timespec timestamp = convertEpicsTimeToUnixTime(pTimeStamp);
      timespec timeNDS;
      timeNDS.tv_sec = pValue[0];
      timeNDS.tv_nsec = pValue[1];

      if (pValue[0] < 0  || pValue[1] < 0) {
        errlogSevPrintf(errlogInfo, 
            "WARNING:: (%s) PV %s, contains values that are too large"
            " to be supported in EPICS, (max_value = %d)",
            __func__, 
            (m_pvs[pasynUser->reason]->getFullNameFromPort()).c_str(),
            std::numeric_limits<std::int32_t>::max());
      }
      m_pvs[pasynUser->reason]->write(timestamp, timeNDS);
      pasynUser->timestamp = pTimeStamp;
      pasynUser->auxStatus = asynSuccess;
      return (asynStatus)pasynUser->auxStatus;
    }

  template <>
    asynStatus EpicsInterfaceImpl::writeArray_NDStypes<std::int32_t, nds::timestamp_t>
        (asynUser *pasynUser, std::int32_t* pValue, size_t /*nElements*/) {
      epicsTimeStamp pTimeStamp;
      pasynManager->updateTimeStamp(pasynUser);
      pasynManager->getTimeStamp(pasynUser,&pTimeStamp);
      timespec timestamp = convertEpicsTimeToUnixTime(pTimeStamp);
      nds::timestamp_t timestampNDS;

      timestampNDS.timestamp.tv_sec = pValue[0];
      timestampNDS.timestamp.tv_nsec  = pValue[1];
      timestampNDS.id = pValue[2];
      timestampNDS.edge = pValue[3];
      if (pValue[0] < 0  || pValue[1] < 0) {
        errlogSevPrintf(errlogInfo, 
            "WARNING:: (%s): PV %s, contains values that are too large"
            " to be supported in EPICS, (max_value = %d)",
            __func__,
            (m_pvs[pasynUser->reason]->getFullNameFromPort()).c_str(),
            std::numeric_limits<std::int32_t>::max());
      }
      m_pvs[pasynUser->reason]->write(timestamp, timestampNDS);
      pasynUser->timestamp = pTimeStamp;
      pasynUser->auxStatus = asynSuccess;
      return (asynStatus)pasynUser->auxStatus;
    }

  template <>
    asynStatus EpicsInterfaceImpl::writeArray_NDStypes<std::int32_t, std::vector<timespec>>
        (asynUser *pasynUser, std::int32_t* pValue, size_t nElements) {
      epicsTimeStamp epicsTimeStamp;
      pasynManager->updateTimeStamp(pasynUser);
      pasynManager->getTimeStamp(pasynUser,&epicsTimeStamp);
      timespec timestamp = convertEpicsTimeToUnixTime(epicsTimeStamp);
      // Check that the number is even
      if (nElements%2 != 0 ) {
          errlogSevPrintf(errlogInfo, 
               "WARNING:: (%s):: Record NELM field must be even for a timespec vector\n", 
               __func__);
      } 
      if (nElements == 0 ) {
          errlogSevPrintf(errlogInfo, 
              "WARNING:: (%s): Record NELM field must be an even positive number\n", 
              __func__);
      } 
      size_t nTs = nElements/2;
      std::vector<timespec> vec_timeNDS(nTs);

      for ( size_t i = 0; i < nTs; i++) {
          vec_timeNDS[i] = {pValue[2*i],pValue[2*i+1]};
        if (pValue[2*i] < 0  || pValue[2*i + 1] < 0) {
          errlogSevPrintf(errlogInfo, 
            "WARNING:: (%s): PV %s, contains values that are too large"
            " to be supported in EPICS, (max_value = %d)",
            __func__, 
            (m_pvs[pasynUser->reason]->getFullNameFromPort()).c_str(),
            std::numeric_limits<std::int32_t>::max());
        }
      }
      m_pvs[pasynUser->reason]->write(timestamp, vec_timeNDS);
      pasynUser->timestamp = epicsTimeStamp;
      pasynUser->auxStatus = asynSuccess;
      return (asynStatus)pasynUser->auxStatus;
    }

  /*
   * Called to write an array into a PV
   *
   ************************************/
  template<typename T>
    asynStatus EpicsInterfaceImpl::writeArray(asynUser *pasynUser, T* pValue, 
        size_t nElements) {
       try {
        nds::dataType_t thisDataType = m_pvs[pasynUser->reason]->getDataType();
        switch(thisDataType) {
          case dataType_t::dataUint32Array:
            return writeArray_NDStypes<T, std::uint32_t> (pasynUser, pValue, nElements);
          case dataType_t::dataUint16Array:
            return writeArray_NDStypes<T, std::uint16_t> (pasynUser, pValue, nElements);
          case dataType_t::dataTimespec:
            return writeArray_NDStypes<std::int32_t, timespec> (pasynUser, 
                (std::int32_t *)pValue, nElements);
          case dataType_t::dataTimestamp:
            return writeArray_NDStypes<std::int32_t, nds::timestamp_t> (pasynUser, 
                (std::int32_t *)pValue, nElements);
          case dataType_t::dataTimespecArray:
            return writeArray_NDStypes<std::int32_t, std::vector<timespec>> (pasynUser, 
                (std::int32_t *)pValue, nElements);
          case dataType_t::dataBoolArray:
            return writeArray_NDStypes<T, bool>(pasynUser, pValue, nElements);
          default:
            return writeArray_NDStypes<T, T>(pasynUser, pValue, nElements);
        }
       } catch(std::runtime_error& e) {
           nds::NdsError *error_nds = dynamic_cast<nds::NdsError*>(&e);
                    if (error_nds == NULL) {
                        pasynUser->auxStatus = asynError;
                    } else {
                        switch (error_nds->status) {
                        case statusPV_t::success:
                            pasynUser->auxStatus = asynSuccess;
                            break;
                        case statusPV_t::timeout:
                            pasynUser->auxStatus = asynTimeout;
                            break;
                        case statusPV_t::overflow:
                            pasynUser->auxStatus = asynOverflow;
                            break;
                        case statusPV_t::disconnected:
                            pasynUser->auxStatus = asynDisconnected;
                            break;
                        case statusPV_t::disabled:
                            pasynUser->auxStatus = asynDisabled;
                            break;
                        case statusPV_t::error:
                            pasynUser->auxStatus = asynError;
                            break;
                        default:
                            pasynUser->auxStatus = asynError;
                        }
                    }
                errorAndSize_t errorAndSize = getErrorString(e.what());
                pasynUser->errorMessage = (char*) errorAndSize.first;
                pasynUser->errorMessageSize = errorAndSize.second;
      }
      return asynError;
      //throw std::logic_error("Array Data could not be written");
    }



  /*********************************************************
   *
   * OVERWRITTEN METHODS FROm asynPortDriver
   *
   *********************************************************/


  asynStatus EpicsInterfaceImpl::readInt32(asynUser *pasynUser, epicsInt32 *pValue)
  {
    return readOneValue<std::int32_t>(pasynUser, (std::int32_t*)pValue);
  }
  asynStatus EpicsInterfaceImpl::readInt64(asynUser *pasynUser, epicsInt64 *pValue)
  {
    return readOneValue<std::int64_t>(pasynUser, (std::int64_t*)pValue);
  }
  asynStatus EpicsInterfaceImpl::readFloat64(asynUser *pasynUser, epicsFloat64 *pValue)
  {
    //Supporting access to ndsCoreFloat32PV and ndsCoreFloat64PV
      asynStatus status;
      if(m_pvs[pasynUser->reason]->getDataType() ==nds::dataType_t::dataFloat32){
          float val;
          status =  readOneValue<float>(pasynUser, &val);
          *pValue = (epicsFloat64)val;
      }else{
          status =  readOneValue<double>(pasynUser, pValue);
      }
          return status;
  }


  asynStatus EpicsInterfaceImpl::writeInt32(asynUser *pasynUser, epicsInt32 value)
  {
    return writeOneValue<std::int32_t>(pasynUser, (std::int32_t)value);
  }
  asynStatus EpicsInterfaceImpl::writeInt64(asynUser *pasynUser, epicsInt64 value)
   {
     return writeOneValue<std::int64_t>(pasynUser, (std::int64_t)value);
   }
  asynStatus EpicsInterfaceImpl::readFloat32(asynUser *pasynUser, epicsFloat64 *pValue)
  {
    return readOneValue<double>(pasynUser, (double*)pValue);
  }

  asynStatus EpicsInterfaceImpl::writeFloat32(asynUser *pasynUser, epicsFloat64 value)
  {
    return writeOneValue<float>(pasynUser, (float)value);
  }

  asynStatus EpicsInterfaceImpl::writeFloat64(asynUser *pasynUser, epicsFloat64 value)
  {
    return writeOneValue<double>(pasynUser, (double)value);
  }

  asynStatus EpicsInterfaceImpl::readInt8Array(asynUser *pasynUser, epicsInt8* pValue,
      size_t nElements, size_t *nIn)
  {
    return readArray<std::int8_t>(pasynUser, (std::int8_t*)pValue, nElements, nIn);
  }

  asynStatus EpicsInterfaceImpl::readInt16Array(asynUser *pasynUser, epicsInt16* pValue,
      size_t nElements, size_t *nIn)
  {
    return readArray<std::int16_t>(pasynUser, (std::int16_t*)pValue, nElements, nIn);
  }

  asynStatus EpicsInterfaceImpl::readInt32Array(asynUser *pasynUser, epicsInt32* pValue,
      size_t nElements, size_t *nIn)
  {
    return readArray<std::int32_t>(pasynUser, (std::int32_t*)pValue, nElements, nIn);
  }
  asynStatus EpicsInterfaceImpl::readInt64Array(asynUser *pasynUser, epicsInt64* pValue,
      size_t nElements, size_t *nIn)
  {
    return readArray<std::int64_t>(pasynUser, (std::int64_t*)pValue, nElements, nIn);
  }
  asynStatus EpicsInterfaceImpl::readFloat32Array(asynUser *pasynUser, epicsFloat32* pValue,
      size_t nElements, size_t *nIn)
  {
    return readArray<float>(pasynUser, (float*)pValue, nElements, nIn);
  }

  asynStatus EpicsInterfaceImpl::readFloat64Array(asynUser *pasynUser, epicsFloat64* pValue,
      size_t nElements, size_t *nIn)
  {
    return readArray<double>(pasynUser, (double*)pValue, nElements, nIn);
  }


  asynStatus EpicsInterfaceImpl::writeInt8Array(asynUser *pasynUser, epicsInt8* pValue,
      size_t nElements)
  {
    return writeArray<std::int8_t>(pasynUser, (std::int8_t*)pValue, nElements);
  }


  asynStatus EpicsInterfaceImpl::writeInt16Array(asynUser *pasynUser, epicsInt16* pValue,
      size_t nElements)
  {
    return writeArray<std::int16_t>(pasynUser, (std::int16_t*)pValue, nElements);
  }

  asynStatus EpicsInterfaceImpl::writeInt32Array(asynUser *pasynUser, epicsInt32* pValue,
      size_t nElements)
  {
    return writeArray<std::int32_t>(pasynUser, (std::int32_t*)pValue, nElements);
  }
  asynStatus EpicsInterfaceImpl::writeInt64Array(asynUser *pasynUser, epicsInt64* pValue,
        size_t nElements)
    {
      return writeArray<std::int64_t>(pasynUser, (std::int64_t*)pValue, nElements);
    }
  asynStatus EpicsInterfaceImpl::writeFloat32Array(asynUser *pasynUser, epicsFloat32* pValue,
      size_t nElements)
  {
    return writeArray<float>(pasynUser, (float*)pValue, nElements);
  }
  asynStatus EpicsInterfaceImpl::writeFloat64Array(asynUser *pasynUser, epicsFloat64* pValue,
      size_t nElements)
  {
    return writeArray<double>(pasynUser, (double*)pValue, nElements);
  }



  asynStatus EpicsInterfaceImpl::drvUserCreate(asynUser *pasynUser, const char *drvInfo,
      const char** /*pptypeName */, size_t* /*psize*/)
  {
    for(size_t scanReasons(0), endReasons(m_pvs.size()); scanReasons != endReasons; ++scanReasons)
    {
      if(m_pvs[scanReasons]->getFullNameFromPort() == drvInfo)
      {
        pasynUser->reason = scanReasons;
        pasynUser->userData = m_pvs[scanReasons].get();
        return asynSuccess;
      }
    }
    return asynError;
  }


  /*
   * Constants used for the EPICS<-->UNIX time conversion
   *
   ******************************************************/
  static const uint64_t nanosecondCoeff(1000000000L);
  static const uint64_t conversionToEpics(uint64_t(POSIX_TIME_AT_EPICS_EPOCH) * nanosecondCoeff);

  /*
   * Conversion from EPICS epoch to UNIX epoch
   *
   *******************************************/
  timespec EpicsInterfaceImpl::convertEpicsTimeToUnixTime(const epicsTimeStamp& time)
  {
    if(time.secPastEpoch == 0 && time.nsec == 0)
    {
      timespec unixTime{0, 0};
      return unixTime;
    }
    //From EPICS to UTC
    std::uint64_t timeNs((std::uint64_t)time.secPastEpoch * nanosecondCoeff + (std::uint64_t)time.nsec + conversionToEpics);

    timespec unixTime;
    unixTime.tv_sec = (std::uint32_t)(timeNs / nanosecondCoeff);
    unixTime.tv_nsec = (std::uint32_t)(timeNs % nanosecondCoeff);

    return unixTime;
  }


  /*
   * Conversion from UNIX epoch to EPICS epoch
   *
   *******************************************/
  epicsTimeStamp EpicsInterfaceImpl::convertUnixTimeToEpicsTime(const timespec& time)
  {
      if(time.tv_sec == 0 && time.tv_nsec == 0)
      {
          epicsTimeStamp epicsTime{0, 0};
          return epicsTime;
      }

      //From UTC to EPICS
      std::uint64_t timeNs((std::uint64_t)time.tv_sec * nanosecondCoeff + (std::uint64_t)time.tv_nsec);
      if(timeNs < conversionToEpics)
      {
          //throw TimeConversionError("The Unix epoch is smaller than the Epics epoch 0");
          epicsTimeStamp epicsTime{0, 0};
          return epicsTime;
      }

      std::uint64_t epicsTimeNs(timeNs - conversionToEpics);

      epicsTimeStamp epicsTime;
      epicsTime.secPastEpoch = epicsTimeNs / nanosecondCoeff;
      epicsTime.nsec = epicsTimeNs % nanosecondCoeff;

      return epicsTime;
  }

  /** Conversion from statusPV_t to asynStatus */
  asynStatus EpicsInterfaceImpl:: convertStatusPVToAsynStatus(const statusPV_t& status) {
    switch (status) {
      case statusPV_t::timeout:
        return asynStatus::asynTimeout;
      case statusPV_t::overflow:
        return asynStatus::asynOverflow;
      case statusPV_t::disconnected:
        return asynStatus::asynDisconnected;
      case statusPV_t::disabled:
        return asynStatus::asynDisabled;
      case statusPV_t::error:
        return asynStatus::asynError;
      case statusPV_t::success:
      default:
        return asynStatus::asynSuccess;
    }
  }

  /*
   * Allocate a static buffer for an error message
   *
   ***********************************************/
  EpicsInterfaceImpl::errorAndSize_t EpicsInterfaceImpl::getErrorString(const std::string& error)
  {
    std::pair<std::set<std::string>::const_iterator, bool> elementInsertion = m_errorMessages.insert(error);
    return errorAndSize_t((*elementInsertion.first).c_str(), (*elementInsertion.first).size());

  }

  void nds::EpicsInterfaceImpl::registerReporter(reporter_t reporter_in) {
      if(reporter==NULL){
    reporter=reporter_in;
      }else {
          errlogSevPrintf(errlogInfo,
                                  "WARNING:: (%s): The driver can only implement one report function.\n",
                                  __func__);
      }
  }

  void nds::EpicsInterfaceImpl::report(FILE* file, int details) {
    if (reporter==NULL)
    {
        errlogSevPrintf(errlogInfo,
                      "WARNING:: (%s): The driver does not implement a report function or did not register it.\n",
                      __func__);
    }
    else{
    reporter(file,details);
    }
  }
}
