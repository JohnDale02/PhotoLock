import json
import subprocess
import base64
import os
import tempfile

def handler(event, context):
    """
    AWS Lambda function handler for processing AVI files and converting them to MP4.
    
    This function:
    1. Receives a base64-encoded AVI file through the event.
    2. Converts the AVI file to MP4 using FFmpeg.
    3. Returns the base64-encoded MP4 file.

    Args:
        event (dict): The event payload containing the base64-encoded AVI file data.
        context (object): AWS Lambda context object (not used in this function).

    Returns:
        dict: A dictionary containing the HTTP status code and the base64-encoded MP4 file.
    """
    try:
        # Parse the incoming event body
        body = json.loads(event['body'])
        
        # Decode the incoming base64 encoded AVI file data
        avi_data = base64.b64decode(body['avi_data'])

        # Get the first 10 and last 10 bytes of the AVI data for debugging purposes
        first_10_bytes = avi_data[:10]
        last_10_bytes = avi_data[-10:]
        
        print("First 10 bytes (hex):", first_10_bytes.hex())
        print("Last 10 bytes (hex):", last_10_bytes.hex())

        # Use a temporary file to store the AVI data
        with tempfile.NamedTemporaryFile(delete=False, suffix='.avi') as temp_avi_file:
            temp_avi_file_path = temp_avi_file.name
            temp_avi_file.write(avi_data)

        # Define the MP4 output path
        temp_mp4_file_path = f"{temp_avi_file_path}.mp4"

        # Convert the AVI file to MP4
        convert_to_mp4(temp_avi_file_path, temp_mp4_file_path)

        # Read the converted MP4 file and encode it to base64
        with open(temp_mp4_file_path, 'rb') as mp4_file:
            mp4_data = mp4_file.read()
        mp4_base64 = base64.b64encode(mp4_data).decode('utf-8')

        # Clean up temporary files
        os.remove(temp_avi_file_path)
        os.remove(temp_mp4_file_path)

        # Return the base64 encoded MP4 file
        return {
            "statusCode": 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type',
            },
            "body": json.dumps({"mp4_base64": mp4_base64})
        }

    except Exception as e:
        # Handle any errors that occur during processing
        print(f"Error: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }

def convert_to_mp4(avi_file_path, mp4_file_path):
    """
    Converts an AVI file to MP4 using FFmpeg.

    Args:
        avi_file_path (str): Path to the input AVI file.
        mp4_file_path (str): Path where the output MP4 file should be saved.
    """
    command = [
        'ffmpeg',
        '-i', avi_file_path,
        '-c:v', 'libx264',
        '-crf', '23',
        '-preset', 'medium',
        '-c:a', 'aac',
        '-b:a', '128k',
        '-y',  # Overwrite output files without asking
        mp4_file_path
    ]
    # Execute the FFmpeg command
    subprocess.run(command, check=True)
