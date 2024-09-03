import boto3

def upload_image(image, metadata):
    """
    Upload an image to an S3 bucket with associated metadata.

    Parameters:
        image (bytes): The image data to be uploaded, typically from a cv2.imread() call.
        metadata (dict): A dictionary of metadata to be associated with the image in S3.

    This function:
    - Creates an S3 client using the boto3 library.
    - Specifies the S3 bucket name and file key (filename) for the upload.
    - Attempts to upload the image to the specified S3 bucket with the associated metadata.
    - Handles any exceptions that occur during the upload process and prints an error message if an exception occurs.
    """
    # Create an S3 client using boto3
    s3_client = boto3.client('s3')

    # Bucket name and file key (filename) details
    bucket_name = 'unverifiedimages'
    file_key = 'NewImage.png'  # This can be dynamically generated if needed

    try:
        # Attempt to upload the image to the S3 bucket with associated metadata
        response = s3_client.put_object(Bucket=bucket_name, Key=file_key, Body=image, Metadata=metadata)
        # If needed, you can print the response for debugging
        # print(f"Response: {response}")

    except Exception as e:
        # Print an error message if the upload fails
        print(f'Exception occurred during upload: {e}')
