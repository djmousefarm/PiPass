#!/usr/bin/python

#### Imported Libraries ####

from xml.dom.minidom import Document
from xml.dom.minidom import parse
import xml.dom.minidom
import subprocess
import time

#### Configuration Variables - Adjust to your Preferences ####

# Hostapd driver for your USB WiFi dongle. If the default value does not work for
# you, you may need to research which driver is compatible. Refer to README at
# https://github.com/Matthew-Hsu/PiPass/blob/master/README.md
HOSTAPD_DRIVER = "nl80211"

# Controls the minutes between each Nintendo Zone cycle.
STREETPASS_CYCLE_MINUTES = 15

#### PiPass Support - MODIFY AT YOUR OWN RISK ####

# Network configuration file path for PiPass to spoof as a Nintendo Zone.
NETWORK_CONFIGURATION = "/etc/hostapd/hostapd.conf"

# Path to the list of current Nintendo Zones being used.
NINTENDO_ZONES = "/var/www/assets/xml/current_zones.xml"

# Path to the XML file where PiPass will write to for the PiPass Dashboard to display connection information.
DASHBOARD_INFO = "/var/www/assets/xml/current_state.xml"

# Flag that informs PiPass that updates have been made to current_zones.xml and to use those updates. Default value is "execute".
piPassStatus = "execute"

# Temporary flag file path for piPassStatus.
FLAG_PATH = "/tmp/pipass_flag.txt"

# Converting STREETPASS_CYCLE_MINUTES to seconds.
STREETPASS_CYCLE_SECONDS = STREETPASS_CYCLE_MINUTES * 60

# Constructing hostapd command string.
COMMAND = "timeout " + str(STREETPASS_CYCLE_SECONDS) + " hostapd " + NETWORK_CONFIGURATION

#### PiPass Main #####

print("[ PiPass - Homepass for the Nintendo 3DS ]\n")

# Ensure that hostapd is running.
subprocess.Popen("sudo service hostapd start", shell=True, stdout=subprocess.PIPE)
print("> Starting up hostapd services...")
time.sleep(5)

# Create/Overwrite flag file for piPassStatus.
fo = open(FLAG_PATH, "w")
fo.write(piPassStatus)
fo.close()

# Open current_zones.xml using minidom parser.
DOMTree = xml.dom.minidom.parse(NINTENDO_ZONES)
collection = DOMTree.documentElement

print("> PiPass is currently running...")

# This loop does not feel pity or remorse or fear and it cannot be stopped unless Half-Life 3 is released.
while "Waiting for Half-Life 3":
    # Get all the Nintendo Zones in the collection.
    zones = collection.getElementsByTagName("ZONE")

    # Begin looping through all the Nintendo Zones in the collection.
    for currentZone in zones:
        # Open the flag file and read in the value.
        fo = open(FLAG_PATH)
        piPassStatus = fo.read()
        fo.close()

        # If the user has issued an update, then reload current_zones.xml for the updated Nintendo Zones.
        if piPassStatus == "update\n":
            # current_zones.xml has been changed, so reload it.
            DOMTree = xml.dom.minidom.parse(NINTENDO_ZONES)
            collection = DOMTree.documentElement

            # We want PiPass to keep running.
            piPassStatus = "execute"

            # Overwrite flag file for piPassStatus.
            fo = open(FLAG_PATH, "w")
            fo.write(piPassStatus)
            fo.close()

            print("\n< Update Detected! - Using new updated Nintendo Zones. >\n")

            break

        # Write the current zone information to NETWORK_CONFIGURATION.
        fo = open(NETWORK_CONFIGURATION, "w")

        currentMAC = currentZone.getElementsByTagName("MAC")[0]
        currentMAC = currentMAC.childNodes[0].data

        currentSSID = currentZone.getElementsByTagName("SSID")[0]
        currentSSID = currentSSID.childNodes[0].data

        currentDesc = currentZone.getElementsByTagName("DESCRIPTION")[0]
        currentDesc = currentDesc.childNodes[0].data

        conf = "interface=wlan0\nbridge=br0\ndriver=" + HOSTAPD_DRIVER + "\nssid=" + currentSSID + "\nbssid=" + currentMAC + "\nhw_mode=g\nchannel=6\nauth_algs=1\nwpa=0\nmacaddr_acl=1\naccept_mac_file=/etc/hostapd/mac_accept\nwmm_enabled=0\nignore_broadcast_ssid=0"

        fo.write(conf)
        fo.close()

        # Nintendo Zone identity acquired for PiPass spoofing.
        print("> Spoofing as " + currentMAC + " on " + currentSSID + " ( " + currentDesc + ") for " + str(STREETPASS_CYCLE_MINUTES) + " minute(s).")

        # Write PiPass status to DASHBOARD_INFO
        doc = Document()
        root = doc.createElement("PI_PASS_STATUS")
        stateXML = {'STATE':'Running', 'MAC':currentMAC, 'SSID':currentSSID, 'DESCRIPTION':currentDesc}

        doc.appendChild(root)

        for value in stateXML:
            # Create Element
            tempChild = doc.createElement(value)
            root.appendChild(tempChild)

            # Write Text
            nodeText = doc.createTextNode(stateXML[value].strip())
            tempChild.appendChild(nodeText)

        doc.writexml(open(DASHBOARD_INFO, 'w'), indent="  ", addindent="  ", newl='\n')
        doc.unlink()

        # Run current Nintendo Zone and pause for STREETPASS_CYCLE_MINUTES until moving onto the next Nintendo Zone.
        subprocess.Popen(COMMAND, shell=True, stdout=subprocess.PIPE)
        time.sleep(STREETPASS_CYCLE_SECONDS)
