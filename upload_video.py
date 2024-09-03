import boto3

def upload_video(video_bytes, metadata):
    """
    Upload a video to an S3 bucket with associated metadata.

    Parameters:
        video_bytes (bytes): The video data to be uploaded in binary format.
        metadata (dict): A dictionary of metadata to be associated with the video in S3.

    This function:
    - Creates an S3 client using the boto3 library.
    - Specifies the S3 bucket name and file key (filename) for the upload.
    - Attempts to upload the video to the specified S3 bucket with the associated metadata.
    - Sets the ContentDisposition to 'attachment' to suggest downloading the file when accessed via a web browser.
    - Handles any exceptions that occur during the upload process and prints an error message if an exception occurs.
    """
    # Create an S3 client using boto3
    s3_client = boto3.client('s3')

    # Bucket name and file key (filename) details
    bucket_name = 'unverifiedimages'
    file_key = 'NewVideo.avi'  # This can be dynamically generated if needed

    try:
        # Attempt to upload the video to the S3 bucket with associated metadata
        response = s3_client.put_object(Bucket=bucket_name, Key=file_key, Body=video_bytes, Metadata=metadata, ContentDisposition='attachment')
        # If needed, you can print the response for debugging
        # print(f"Upload successful. Response: {response}")

    except Exception as e:
        # Print an error message if the upload fails
        print(f'We had an exception: {e}')
