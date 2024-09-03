from pyfingerprint.pyfingerprint import PyFingerprint
import time

try:
    ## Initialize the fingerprint sensor on the specified UART port.
    ## Change here: Update the port to '/dev/ttyAMA1' or the correct one for UART4 if needed.
    f = PyFingerprint('/dev/ttyAMA5', 57600, 0xFFFFFFFF, 0x00000000)

    ## Verify the sensor's password.
    if not f.verifyPassword():
        raise ValueError('The given fingerprint sensor password is incorrect!')

except Exception as e:
    print('The fingerprint sensor could not be initialized!')
    print('Exception message: ' + str(e))
    exit(1)

try:
    print('Waiting for finger...')
    ## Wait until a finger is read by the sensor.
    while not f.readImage():
        pass

    ## Convert the read image to characteristics and store it in charbuffer 1.
    f.convertImage(0x01)

    # Optionally, search if the fingerprint is already enrolled.
    # result = f.searchTemplate()
    # positionNumber = result[0]

    # if positionNumber >= 0:
    #     print('Template already exists at position #' + str(positionNumber))
    #     exit(0)

    print('Remove finger...')
    time.sleep(2)  # Pause for a moment to allow the user to remove their finger.

    print('Waiting for the same finger again...')
    ## Wait until the same finger is read again.
    while not f.readImage():
        pass

    ## Convert the read image to characteristics and store it in charbuffer 2.
    f.convertImage(0x02)

    ## Compare the characteristics in charbuffer 1 and charbuffer 2.
    if f.compareCharacteristics() == 0:
        raise Exception('Fingers do not match')

    ## Create a template from the characteristics in charbuffer 1 and 2.
    f.createTemplate()

    ## Store the template in the sensor's memory and retrieve the position number.
    positionNumber = f.storeTemplate()
    print('Finger enrolled successfully!')
    print('New template position #' + str(positionNumber))

except Exception as e:
    print('Operation failed!')
    print('Exception message: ' + str(e))
    exit(1)
