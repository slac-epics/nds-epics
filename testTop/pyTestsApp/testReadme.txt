**Tests by UPM readme
*Author: Miguel Astrain

Some nodes have a high count of PVs and functionality. To test these nodes a semi-automated testing python programs can be found in this file.

The purpose of these tests is NOT to test full node functionality but to cover as much as possible, and more importantly, to make sure all the PVs can be accessed 
(either write or read operation.)

GenericTestTemplate.py is a generic test with some comments to be modified and adapted.

There are 5 nodes tested in this way:
-testNdsWaveFormgGeneration
-testNdsDataAcquisition
-testNdsDigitalIO
-testNdsRouting
-testNdsFTE

They are all based on the Generic template and have the same structure: 

IOC is started with data about the device name, the shared library name, the node name and the sustitution file name. 
These can be modified in the "def setUP)" definition.

 
 '''Other test utilities'''
 Here a userList list is defined with (PVname, DataToTest) pairs.
 The IOC is running and the dbl list is dumped to a file for debugging purposes, these are deleted at the end.
'''------------------------check if userList constains pvList--------------'''
We check that all the IOC PVs will be tested with the provided list.
'''-----------------------Define custom test procedure---------------------'''
We list the PVs by reading them using "caget" for each "pvname" on the pvlist. 
If run as a python program this will print outputs to screen.
Then the list is iterated to try putting the values of the pvlist.
Camonitor is up for all the PVs in the list during this loop.
Some PVs are expected to update when written other are not and will timeout. This is expected bahavior.
At the end the whole list is retrieved again and checked for tiemstamp updates. If all the records have been processed we exit as OK, if not it fails.
This test does not check values. The node functionality is checked on the NDS-Core test framework with google tests.
The goal is to check we can communicate and interact with all the PVs.   