#!/usr/bin/env python

# IMPORT

from __future__ import print_function
import sys
import os
import time
from abc import abstractmethod

from blue_st_sdk.manager import Manager
from blue_st_sdk.manager import ManagerListener
from blue_st_sdk.node import NodeListener
from blue_st_sdk.feature import FeatureListener
from blue_st_sdk.features.audio.adpcm.feature_audio_adpcm import FeatureAudioADPCM
from blue_st_sdk.features.audio.adpcm.feature_audio_adpcm_sync import FeatureAudioADPCMSync


# PRECONDITIONS
#
# In case you want to modify the SDK, clone the repository and add the location
# of the "BlueSTSDK_Python" folder to the "PYTHONPATH" environment variable.
#
# On Linux:
#   export PYTHONPATH=/home/<user>/BlueSTSDK_Python


# CONSTANTS

# Presentation message.
INTRO = """##############
# Start Gyro #   
##############"""

# Bluetooth Scanning time in seconds (optional).
SCANNING_TIME_s = 2 #5

# Mac adress to auto connect
MAC_AUTO_CONNEXION = "cd:26:fb:e4:6d:f1"

# Feature to auto start : "Temperature", "Humidity", "Pressure", "Magnetometer", "Gyroscope", "Accelerometer", "Proximity", "Audio & Sync", "Switch"
FEATURE_AUTO_START = ["Gyroscope", "Proximity"] #  or ["Temperature", "Humidity", "Pressure"] or [] to use manualy

# FUNCTIONS

#
# Printing intro.
#
def print_intro():
    print('\n' + INTRO + '\n')


# INTERFACES

#
# Implementation of the interface used by the Manager class to notify that a new
# node has been discovered or that the scanning starts/stops.
#
class MyManagerListener(ManagerListener):

    #
    # This method is called whenever a discovery process starts or stops.
    #
    # @param manager Manager instance that starts/stops the process.
    # @param enabled True if a new discovery starts, False otherwise.
    #
    def on_discovery_change(self, manager, enabled):
        print('[+] Discovery %s.' % ('started' if enabled else 'stopped'))
        if not enabled:
            print()

    #
    # This method is called whenever a new node is discovered.
    #
    # @param manager Manager instance that discovers the node.
    # @param node    New node discovered.
    #
    def on_node_discovered(self, manager, node):
        print('[+] New device discovered: %s.' % (node.get_name()))


#
# Implementation of the interface used by the Node class to notify that a node
# has updated its status.
#
class MyNodeListener(NodeListener):

    #
    # To be called whenever a node connects to a host.
    #
    # @param node Node that has connected to a host.
    #
    def on_connect(self, node):
        print('[+] Device %s connected.' % (node.get_name()))

    #
    # To be called whenever a node disconnects from a host.
    #
    # @param node       Node that has disconnected from a host.
    # @param unexpected True if the disconnection is unexpected, False otherwise
    #                   (called by the user).
    #
    def on_disconnect(self, node, unexpected=False):
        print('[+] Device %s disconnected%s.' % \
            (node.get_name(), ' unexpectedly' if unexpected else ''))
        if unexpected:
            # Exiting.
            print('\n[+] Exiting...\n')
            sys.exit(0)


#
# Implementation of the interface used by the Feature class to notify that a
# feature has updated its data.
#
class MyFeatureListener(FeatureListener):

    #
    # To be called whenever the feature updates its data.
    #
    # @param feature Feature that has updated.
    # @param sample  Data extracted from the feature.
    #
    def on_update(self, feature, sample):
            print(feature)
            # feature name : feature.get_name()
            # Data are in : sample.get_data()
            # Timestamp : sample.get_timestamp()
            #TODO data output (fifo ?) : 
            if feature.get_name() == "Temperature":
                out_temp = sample.get_data()
            elif feature.get_name() == "Humidity":
                out_temp = sample.get_data()
            elif feature.get_name() == "Pressure":
                out_temp = sample.get_data()
            elif feature.get_name() == "Magnetometer":
                out_temp_x = sample.get_data()[0]
                out_temp_y = sample.get_data()[1]
                out_temp_z = sample.get_data()[2]
            elif feature.get_name() == "Gyroscope":
                out_temp_x = sample.get_data()[0]
                out_temp_y = sample.get_data()[1]
                out_temp_z = sample.get_data()[2]
            elif feature.get_name() == "Accelerometer":
                out_temp_x = sample.get_data()[0]
                out_temp_y = sample.get_data()[1]
                out_temp_z = sample.get_data()[2]
            elif feature.get_name() == "Proximity":
                out_temp = sample.get_data()
            elif feature.get_name() == "Audio & Sync":
                pass
            elif feature.get_name() == "Switch":
                pass


# MAIN APPLICATION

#
# Main application.
#
def main(argv):

    # Printing intro.
    print_intro()

    try:
        # Creating Bluetooth Manager.
        manager = Manager.instance()
        manager_listener = MyManagerListener()
        manager.add_listener(manager_listener)

        while True:
            discovered_devices_once = []
            no_connect = True
            no_feature_select = True
            feature_selected = []

            # Asynchronous discovery of Bluetooth devices.
            print('[+] Scanning Bluetooth devices...\n')
            manager.start_discovery()
            timeout = time.time() + SCANNING_TIME_s
            while no_connect:
                time.sleep(0.01)

                # Getting discovered devices.
                discovered_devices = manager.get_nodes()

                i = 1
                for device in discovered_devices:
                    if device.get_tag() not in discovered_devices_once: 
                        print('[+] %s: [%s]' % (device.get_name(), device.get_tag()))
                        discovered_devices_once.append(device.get_tag())
                        # Autoconnection management
                        if device.get_tag() == MAC_AUTO_CONNEXION:
                            print('[+] Device MAC address match')
                            no_connect = False
                            choice = i
                        i += 1
                # Timeout management
                if time.time() > timeout:
                    break
            manager.stop_discovery()

            # Selecting a device.
            while no_connect:
                print('[+] Available Bluetooth devices:')
                i = 1
                for device in discovered_devices:
                    print('[+] %d) %s: [%s]' % (i, device.get_name(), device.get_tag()))
                    i += 1
                choice = int(input("\nSelect a device to connect to (\'0\' to quit): "))
                if choice >= 0 and choice <= len(discovered_devices):
                    no_connect = False
            if choice == 0:
                # Exiting.
                manager.remove_listener(manager_listener)
                print('[+] Exiting...\n')
                sys.exit(0)
            device = discovered_devices[choice - 1]
            node_listener = MyNodeListener()
            device.add_listener(node_listener)

            # Connecting to the device.
            print('[+] Connecting to %s...' % (device.get_name()))
            if not device.connect():
                print('[+] Connection failed.\n')
                continue

            while True:
                # Getting features.
                features = device.get_features()
                print('\n[+] Features:')
                i = 1
                for feature in features:
                    if feature.get_name() in FEATURE_AUTO_START:
                        print('[+] Feature matching - %s' % (feature.get_name()))
                        choice = i
                        feature_selected.append(i)
                        no_feature_select = False

                    if isinstance(feature, FeatureAudioADPCM):
                        audio_feature = feature
                        print('[+] %d,%d) %s' % (i,i+1, "Audio & Sync"))
                        i+=1
                    elif isinstance(feature, FeatureAudioADPCMSync):
                        audio_sync_feature = feature
                    else:
                        print('[+] %d) %s' % (i, feature.get_name()))
                        i+=1

                # Selecting a feature.
                while no_feature_select:
                    choice = int(input('\nSelect a feature ''(\'0\' to disconnect): '))
                    if choice >= 0 and choice <= len(features):
                        feature_selected.append(choice)
                        no_feature_select = False
                        
                if len(feature_selected) == 0:
                    # Disconnecting from the device.
                    print('\n[+] Disconnecting from %s...' % (device.get_name()))
                    if not device.disconnect():
                        print('[+] Disconnection failed.\n')
                        continue
                    device.remove_listener(node_listener)
                    # Resetting discovery.
                    manager.reset_discovery()
                    # Going back to the list of devices.
                    break

                for feature_id in feature_selected:
                    feature = features[feature_id - 1]
                    # Enabling notifications.
                    feature_listener = MyFeatureListener()  
                    feature.add_listener(feature_listener)
                    device.enable_notifications(feature)

                # Handling audio case (both audio features have to be enabled).
                if isinstance(feature, FeatureAudioADPCM):
                    audio_sync_feature_listener = MyFeatureListener()
                    audio_sync_feature.add_listener(audio_sync_feature_listener)
                    device.enable_notifications(audio_sync_feature)
                elif isinstance(feature, FeatureAudioADPCMSync):
                    audio_feature_listener = MyFeatureListener()
                    audio_feature.add_listener(audio_feature_listener)
                    device.enable_notifications(audio_feature)

                # Getting notifications.
                while True:
                    device.wait_for_notifications(10)
                    #TODO break management

                # TODO : clean disabling (array of feature/feature_listener)
                # Disabling notifications.
                device.disable_notifications(feature)
                feature.remove_listener(feature_listener)
                
                # Handling audio case (both audio features have to be disabled).
                if isinstance(feature, FeatureAudioADPCM):
                    device.disable_notifications(audio_sync_feature)
                    audio_sync_feature.remove_listener(audio_sync_feature_listener)
                elif isinstance(feature, FeatureAudioADPCMSync):
                    device.disable_notifications(audio_feature)
                    audio_feature.remove_listener(audio_feature_listener)

    except KeyboardInterrupt:
        try:
            # Exiting.
            print('\n[+] Exiting...\n')
            sys.exit(0)
        except SystemExit:
            os._exit(0)


if __name__ == "__main__":

    main(sys.argv[1:])
