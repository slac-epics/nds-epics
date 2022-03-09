TOP=../..
include $(TOP)/configure/CONFIG
#----------------------------------------
#  ADD MACRO DEFINITIONS AFTER THIS LINE

#----------------------------------------------------
#  Optimization of db files using dbst (DEFAULT: NO)
#DB_OPT = YES

#----------------------------------------------------
# Create and install (or just install) into <top>/db
# databases, templates, substitutions like this
DB += nds3_DataAcquisition.template
DB += nds3_DataGeneration.template
DB += nds3_DataMultiplexing.template
DB += nds3_DataScheduling_ChannelOut.template
DB += nds3_DataScheduling.template
DB += nds3_DigitalIO.template
DB += nds3_FTE.template
DB += nds3_WaveForm.template
DB += nds3_Routing.template
DB += nds3_StateMachine.template
DB += nds3_Firmware.template
DB += nds3_HQMonitor.template
DB += nds3_Timestamping.template
DB += nds3_DevicePV.template
DB += nds3_Timing.template
DB += nds3_TrigAndClk.template
DB += nds3_DeviceError.template

#----------------------------------------------------
# If <anyname>.db template is not named <anyname>*.template add
# <anyname>_template = <templatename>

include $(TOP)/configure/RULES
#----------------------------------------
#  ADD RULES AFTER THIS LINE

