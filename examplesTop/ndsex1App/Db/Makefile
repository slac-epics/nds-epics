TOP=../..
include $(TOP)/configure/CONFIG
#----------------------------------------
#  ADD MACRO DEFINITIONS AFTER THIS LINE

#----------------------------------------------------
#  Optimization of db files using dbst (DEFAULT: NO)
#DB_OPT = YES

#----------------------------------------------------
# Create and install (or just install)
# databases, templates, substitutions like this
DB+=DataAcquisition.substitutions
DB+=DataGeneration.substitutions
DB+=DigitalIO.substitutions
DB+=WaveForm.substitutions
DB+=FTE.substitutions
DB+=Routing.substitutions
DB+=TrigAndClk.substitutions
DB+=exampleDrv.substitutions
DB+=exampleDrv.template
DB+=DeviceDataMultiplexing.template
DB+=DeviceDataMultiplexing.substitutions
DB+=DeviceError.substitutions
DB+=nds3_DeviceError.template
#----------------------------------------------------
# If <anyname>.db template is not named <anyname>*.template add
# <anyname>_TEMPLATE = <templatename>

include $(TOP)/configure/RULES
#----------------------------------------
#  ADD RULES AFTER THIS LINE
