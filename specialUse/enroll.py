#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PyFingerprint Finger Enrollment Script
This script enrolls a new fingerprint using the PyFingerprint sensor.

Copyright (C) 2015 Bastian Raschke <bastian.raschke@posteo.de>
All rights reserved.
"""

import time
from pyfingerprint.pyfingerprint import PyFingerprint

## Initialize the fingerprint sensor
try:
    # Create a PyFingerprint object with the specified serial port and settings
    f = PyFingerprint('/dev/ttyAMA5', 57600, 0xFFFFFFFF, 0x00000000)

    # Verify the sensor's password
    if f.verifyPassword() == False:
        raise ValueError('The given fingerprint sensor password is wrong!')

except Exception as e:
    # Handle initialization errors
    print('The fingerprint sensor could not be initialized!')
    print('Exception message: ' + str(e))
    exit(1)

## Get sensor information
print('Currently used templates: ' + str(f.getTemplateCount()) + '/' + str(f.getStorageCapacity()))

## Start the fingerprint enrollment process
try:
    print('Waiting for finger...')

    ## Wait for the finger to be placed on the sensor
    while f.readImage() == False:
        pass

    ## Convert the read image to characteristics and store it in charbuffer 1
    f.convertImage(0x01)
    f.createTemplate()  # Create a template from the image

    ## Check if the fingerprint is already enrolled
    result = f.searchTemplate()
    positionNumber = result[0]

    if positionNumber >= 0:
        print('Template already exists at position #' + str(positionNumber))
        exit(0)

    print('Remove finger...')
    time.sleep(2)

    print('Waiting for the same finger again...')

    ## Wait for the finger to be placed on the sensor again
    while f.readImage() == False:
        pass

    ## Convert the read image to characteristics and store it in charbuffer 2
    f.convertImage(0x02)
    f.createTemplate()  # Create a template from the image

    ## Compare the characteristics in charbuffer 1 and charbuffer 2
    if f.compareCharacteristics() == 0:
        raise Exception('Fingers do not match')

    ## Create a template from the combined characteristics
    f.createTemplate()

    ## Save the template in the next available position
    positionNumber = f.storeTemplate()
    print('Finger enrolled successfully!')
    print('New template position #' + str(positionNumber))

except Exception as e:
    # Handle errors during the enrollment process
    print('Operation failed!')
    print('Exception message: ' + str(e))
    exit(1)
