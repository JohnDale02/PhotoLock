import mysql.connector
import json
import cv2
import hashlib
import os
import base64
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.exceptions import InvalidSignature

def handler(event, context):
    """
    AWS Lambda function to verify the signature of an image or video uploaded to a Twitter clone project.

    This function decodes the media from the incoming request, extracts metadata from the database,
    verifies the signature, and returns whether the media is valid or not along with its metadata if valid.

    Args:
        event (dict): The event payload containing media data and metadata.
        context (object): AWS Lambda context object (not used in this function).

    Returns:
        dict: A dictionary containing the HTTP status code and the result of the verification process.
    """
    errors = ""
    print("THIS IS THE VERIFICATION API CALL")
    try:
        # Parse the JSON string in the body
        body = json.loads(event['body'])

        content_type = body['type']
        # Access the 'image' or 'video' key directly
        binary_media  = base64.b64decode(body['image'])

    except Exception as e:
        errors = "Error decoding media from event: " + str(e)
    
    if content_type == "image/png":
        # Process image
        try:
            image = binary_image_to_numpy(binary_media)
            _, encoded_image = cv2.imencode('.png', image)
            encoded_media = encoded_image.tobytes()

        except Exception as e:
            errors += f"Error converting binary image to numpy: {str(e)}"

        try:
            details = get_json_details(binary_media)
            if details:
                fingerprint = details[0]
                camera_number = details[1]
                date_data = details[2]
                time_data = details[3]
                location_data = details[4]
                signature_string = details[5]
                signature = base64.b64decode(signature_string)

        except Exception as e:
            errors += f"Error getting JSON details: {str(e)}"

        try:
            combined_data = create_combined(fingerprint, camera_number, encoded_media, date_data, time_data, location_data)
        
        except Exception as e:
            errors += f"Error combining data: {str(e)}"

        try:
            public_key_base64 = get_public_key(int(camera_number))
            public_key = base64.b64decode(public_key_base64)

        except Exception as e:
            errors += f"Public key error: {str(e)}"

        try: 
            valid = verify_signature(combined_data, signature, public_key)

        except Exception as e:
            valid = False  # Something went wrong verifying the signature
            errors += f"Error verifying or denying signature: {str(e)}"

        try:
            if valid:
                # Return true with metadata
                return {
                    'statusCode': 200,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({
                        "result": "True",
                        "metadata": {
                            "fingerprint": fingerprint,
                            "camera_number": camera_number,
                            "date_data": date_data,
                            "time_data": time_data,
                            "location_data": location_data,
                            "signature": signature_string
                        }
                    })
                }
            else:
                # Return false without metadata
                return {
                    'statusCode': 200,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({"result": "False"})
                }

        except Exception as e:
            errors = "Unhandled exception: " + str(e)
            return {
                'statusCode': 500,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({"error": errors})
            }

    else:  # Content type is video/avi
        # Process video
        try:
            details = get_json_details(binary_media)
            if details:
                fingerprint = details[0]
                camera_number = details[1]
                date_data = details[2]
                time_data = details[3]
                location_data = details[4]
                signature_string = details[5]
                signature = base64.b64decode(signature_string)

        except Exception as e:
            errors += f"Error getting JSON details for video: {str(e)}"

        try:
            combined_data = create_combined(fingerprint, camera_number, binary_media, date_data, time_data, location_data)
        
        except Exception as e:
            errors += f"Error combining data: {str(e)}"

        try:
            public_key_base64 = get_public_key(int(camera_number))
            public_key = base64.b64decode(public_key_base64)

        except Exception as e:
            errors += f"Public key error: {str(e)}"

        try: 
            valid = verify_signature(combined_data, signature, public_key)

        except Exception as e:
            valid = False  # Something went wrong verifying the signature
            errors += f"Error verifying or denying signature: {str(e)}"

        try:
            if valid:
                # Return true with metadata
                return {
                    'statusCode': 200,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({
                        "result": "True",
                        "metadata": {
                            "fingerprint": fingerprint,
                            "camera_number": camera_number,
                            "date_data": date_data,
                            "time_data": time_data,
                            "location_data": location_data,
                            "signature": signature_string
                        }
                    })
                }
            else:
                # Return false without metadata
                return {
                    'statusCode': 200,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({"result": "False"})
                }

        except Exception as e:
            errors = "Unhandled exception: " + str(e)
            return {
                'statusCode': 500,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({"error": errors})
            }

def get_hash_for_query(binary_image):
    """
    Generates a SHA-256 hash for the provided binary image.

    Args:
        binary_image (bytes): The binary image data.

    Returns:
        str: The SHA-256 hash of the image.
    """
    hash_object = hashlib.sha256()
    hash_object.update(binary_image)
    image_hash = hash_object.hexdigest()

    return image_hash

def binary_image_to_numpy(binary_image):
    """
    Converts a binary image to a NumPy array.

    Args:
        binary_image (bytes): The binary image data.

    Returns:
        numpy.ndarray: The image as a NumPy array.
    """
    temp_file_path = "/tmp/my_temp_file.png"

    with open(temp_file_path, 'wb') as file:
        file.write(binary_image)

    image = cv2.imread(temp_file_path)
    os.remove(temp_file_path)

    return image

def get_json_details(binary_image):
    """
    Retrieves JSON details associated with a given binary image from the database.

    Args:
        binary_image (bytes): The binary image data.

    Returns:
        list: A list containing the fingerprint, camera number, date, time, location, and signature.
        bool: False if no matching hash is found in the database.
    """
    # Hash the image data to use as an index
    image_hash = get_hash_for_query(binary_image)

    # Database connection details
    host = "publickeycamerastorage.c90gvpt3ri4q.us-east-2.rds.amazonaws.com"
    user = "sdp"
    password = "sdpsdpsdp"
    database = "PublicKeySchema"

    # Connect to the database
    connection = mysql.connector.connect(
        host=host, user=user, password=password, database=database
    )
    cursor = connection.cursor()

    # SQL query to retrieve the data for the given image_hash
    query = "SELECT data FROM image_data WHERE image_hash = %s"

    cursor.execute(query, (str(image_hash),))

    # Fetch the result
    result = cursor.fetchone()
    cursor.close()
    connection.close()

    if result:  # If the image_hash is found in the database
        data = json.loads(result[0])
        fingerprint = data.get("Fingerprint")
        camera_number = data.get("Camera Number")
        date_data = data.get("Date")
        time_data = data.get("Time")
        location_data = data.get("Location")
        signature = data.get("Signature_Base64")

        print("Fingerprint: ", fingerprint)
        print("Camera Number: ", camera_number)
        print("Date: ", date_data)
        print("Time: ", time_data)
        print("Location: ", location_data)
        print("Signature: ", signature)

        return [fingerprint, camera_number, date_data, time_data, location_data, signature]
    
    return False  # If the image_hash is not found in the database

def create_combined(fingerprint, camera_number, media, date, time, location):
    """
    Combines provided data into a single byte object.

    Args:
        fingerprint (str): The fingerprint data.
        camera_number (str): The camera number.
        media (bytes): The media file data.
        date (str): The date of the media capture.
        time (str): The time of the media capture.
        location (str): The location of the media capture.

    Returns:
        bytes: The combined byte object containing all provided data.
    """
    encoded_fingerprint = fingerprint.encode('utf-8')
    encoded_number = camera_number.encode('utf-8')
    encoded_date = date.encode('utf-8')
    encoded_time = time.encode('utf-8')
    encoded_location = location.encode('utf-8')

    combined_data = encoded_fingerprint + encoded_number + media + encoded_date + encoded_time + encoded_location

    return combined_data

def get_public_key(camera_number):
    """
    Retrieves the public key associated with a given camera number from the database.

    Args:
        camera_number (int): The camera number.

    Returns:
        str: The public key in PEM format, or an error message if not found.
    """
    # Database connection details
    host = "publickeycamerastorage.c90gvpt3ri4q.us-east-2.rds.amazonaws.com"
    user = "sdp"
    password = "sdpsdpsdp"
    database = "PublicKeySchema"

    # Connect to the database
    connection = mysql.connector.connect(
        host=host, user=user, password=password, database=database
    )
    cursor = connection.cursor()

    # SQL query to retrieve the public key
    query = "SELECT PublicKey FROM Cameras WHERE CameraNumber = %s"

    cursor.execute(query, (int(camera_number),))

    # Fetch the result
    result = cursor.fetchone()
    cursor.close()
    connection.close()

    if result:
        public_key = result[0]
        return public_key  # Return the public key
    
    return 'Public key not found'

def verify_signature(combined_data, signature, public_key):
    """
    Verifies the digital signature of the combined data using the provided public key.

    Args:
        combined_data (bytes): The combined data that was signed.
        signature (bytes): The signature to verify.
        public_key (bytes): The public key to use for verification.

    Returns:
        bool: True if the signature is valid, False otherwise.
    """
    temp_public_key_path = '/tmp/recreated_public_key.pem'

    with open(temp_public_key_path, "wb") as file:
        file.write(public_key)

    with open(temp_public_key_path, "rb") as key_file:
        public_key_data = key_file.read()

    # Deserialize the public key from PEM format
    public_key = serialization.load_pem_public_key(public_key_data)

    try:
        public_key.verify(
            signature,
            combined_data,
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        os.remove(temp_public_key_path)
        return True
    
    except InvalidSignature:
        os.remove(temp_public_key_path)
        return False
