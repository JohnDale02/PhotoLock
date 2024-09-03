import sys
from pyfingerprint.pyfingerprint import PyFingerprint

# Check if the correct number of command-line arguments is provided
if len(sys.argv) < 2:
    print("Usage: python script.py <position_number>")
    exit(1)

# Convert the command-line argument to an integer (position number)
positionNumber = int(sys.argv[1])

try:
    ## Initialize the fingerprint sensor
    # Create an instance of the PyFingerprint class, specifying the serial port and settings
    f = PyFingerprint('/dev/ttyAMA5', 57600, 0xFFFFFFFF, 0x00000000)

    # Verify that the sensor's password is correct
    if (f.verifyPassword() == False):
        raise ValueError('The given fingerprint sensor password is wrong!')

except Exception as e:
    # Handle exceptions during sensor initialization
    print('The fingerprint sensor could not be initialized!')
    print('Exception message: ' + str(e))
    exit(1)

try:
    ## Attempt to delete the fingerprint template at the specified position
    if (f.deleteTemplate(positionNumber) == True):
        print('Template deleted successfully!')
    else:
        print('Failed to delete template!')

except Exception as e:
    # Handle exceptions during the delete operation
    print('Operation failed!')
    print('Exception message: ' + str(e))
    exit(1)
