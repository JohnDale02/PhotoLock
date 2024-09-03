def create_metadata(fingerprint: str, camera_number: str, date_data: str, time_data: str, location_data: str, signature_string: bytes) -> dict:
    """
    Creates a dictionary containing all metadata, including fingerprint, camera number, date, time, location, and signature.

    This function takes in several pieces of information, such as fingerprint, camera number, date, time, location,
    and a signature string (in bytes), and compiles them into a dictionary for easy access and storage.

    Args:
        fingerprint (str): The unique identifier or fingerprint.
        camera_number (str): The camera number.
        date_data (str): The date information.
        time_data (str): The time information.
        location_data (str): The location information.
        signature_string (bytes): The signature, represented as a base64-encoded byte string.

    Returns:
        dict: A dictionary containing all the provided metadata.
    """

    # Initialize an empty dictionary to store metadata
    metadata = {}
    
    # Store each piece of information in the dictionary with a descriptive key
    metadata['Fingerprint'] = fingerprint
    metadata['CameraNumber'] = camera_number
    metadata['Date'] = date_data
    metadata['Time'] = time_data
    metadata['Location'] = location_data
    metadata['Signature'] = signature_string

    # Return the populated metadata dictionary
    return metadata
