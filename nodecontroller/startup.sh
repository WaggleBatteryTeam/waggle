#!/bin/bash
#This starts all necessary parts of the nodecontroller

cd waggle/nodecontroller/nc-wag-os/waggled/
#scan for node's IP and write to a file
python NC_scanner.py
cd ..
cd DataCache
#start the Data Data_Cache
python Data_Cache.py start 
cd ..
cd Communications
#start the background_comms
./background_comms.sh 
cd ..
cd NC
#start receiving messages
./receive_msgs.sh