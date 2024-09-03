import cv2

def create_image():
    """
    Captures an image using the camera, saves it to a file, and returns the image data as a frame.

    This function uses the `capture_image` function to capture an image from the camera.
    If the image is successfully captured, it saves the image to a file named 'NewImage.png'
    and returns the image data as a frame. If the image capture fails, it returns None.

    Returns:
        numpy.ndarray or None: The captured image data as a frame, or None if the capture fails.
    """

    # Capture an image from the camera
    image = capture_image()

    if image is not None:
        print("\tImage not None, Saving...")
        # Save the captured image to a file
        image_filename = "NewImage.png"
        cv2.imwrite(image_filename, image)

        return image
    
    else:
        print("Image is None")
        return None


def capture_image():
    """
    Initializes the camera and captures a single image.

    This function initializes the camera using OpenCV's VideoCapture, captures a single frame,
    and then releases the camera. If the capture is successful, it returns the frame. Otherwise,
    it returns None.

    Returns:
        numpy.ndarray or None: The captured image frame, or None if the capture fails.
    """

    # Initialize the camera (use the appropriate video device, usually 0 for the default camera)
    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        print("\tError: Camera not found or could not be opened.")
        return None

    # Capture a single frame from the camera
    ret, frame = camera.read()
    camera.release()  # Release the camera after capturing the image

    if ret:
        return frame
    else:
        print("\tError: Failed to capture an image.")
        return None
