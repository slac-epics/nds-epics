TOP=..

include $(TOP)/configure/CONFIG
#----------------------------------------
#  ADD MACRO DEFINITIONS AFTER THIS LINE
#=============================

TESTSCRIPTS_HOST += ioctests.py
TESTSCRIPTS_HOST += iocControl.py



CLEANS += *.pyc

include $(TOP)/configure/RULES
#----------------------------------------
#  ADD RULES AFTER THIS LINE

ifeq ($(BASE_3_14),YES)
clean::
	@$(RM) $(CLEANS)
endif

#runtests:
#	nosetests

#tapfiles:
#	nosetests --with-tap

%.py: ../%.py
	$(ECHO) "Copying test script $@"
	@$(INSTALL) -m $(INSTALL_PERMISSIONS) $< .

