from pyfingerprint.pyfingerprint import PyFingerprint

def get_fingerprint(user_number: int) -> int:
    """
    Captures a fingerprint image, searches for a match in the fingerprint sensor's database,
    and returns the position number of the matched template.

    This function initializes the fingerprint sensor, waits for the user to place a finger on the sensor,
    captures the fingerprint image, and compares it against the stored templates in the sensor's database.
    If a match is found, the function returns the position number of the matched template. If no match is found,
    it returns the provided user number minus one.

    Args:
        user_number (int): The user's identification number to return if no match is found.

    Returns:
        int: The position number of the matched template, or user_number - 1 if no match is found.
    """

    try:
        ## Initialize the fingerprint sensor (update the port to '/dev/ttyAMA4' if needed)
        f = PyFingerprint('/dev/ttyAMA5', 57600, 0xFFFFFFFF, 0x00000000)

        # Verify the sensor's password
        if not f.verifyPassword():
            raise ValueError('The given fingerprint sensor password is wrong!')

    except Exception as e:
        # Handle initialization errors
        print('The fingerprint sensor could not be initialized!')
        print('Exception message: ' + str(e))
        exit(1)

    try:
        print('Waiting for finger...')

        # Wait until the finger is placed on the sensor
        while not f.readImage():
            pass

        # Convert the read image to characteristics and store them in charbuffer 1
        f.convertImage(0x01)
        # Search for a matching template in the sensor's database
        result = f.searchTemplate()

        positionNumber = result[0]
        accuracyScore = result[1]

        if positionNumber == -1:
            # No matching fingerprint template found
            print('No match found!')
            return user_number - 1
        else:
            # Matching fingerprint template found
            print('Found template at position #' + str(positionNumber))
            print('The accuracy score is: ' + str(accuracyScore))
            return positionNumber

    except Exception as e:
        # Handle errors during the fingerprint matching process
        print('Operation failed!')
        print('Exception message: ' + str(e))
        exit(1)
