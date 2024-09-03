import threading 
from threading import Lock, Thread, Condition
import RPi.GPIO as GPIO
import time
import subprocess
import cv2
import os
from main import main
from GPS_uart import read_gps_data
from upload_image import upload_image
from upload_video import upload_video
from get_fingerprint import get_fingerprint
import json

from kivy.config import Config
Config.set('graphics', 'width', '800')
Config.set('graphics', 'height', '480')
Config.set('graphics', 'fullscreen', 'auto')

# Importing Kivy components for GUI
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.image import Image  # Use AsyncImage for potentially better handling of image loading
from kivy.graphics.texture import Texture
from kivy.graphics import Color, Rectangle, Ellipse
from kivy.uix.boxlayout import BoxLayout
from kivy.animation import Animation
from kivy.clock import Clock

from kivy.core.window import Window
Window.show_cursor = False

# -------------Global Variables ------------------------------
image_mode = True
ffmpeg_process = None
record_button = 40
mode_button = 38

wifi_status = False
gps_status = False

ignore_button_presses = False  # Flag to indicate whether to ignore button events
recording_indicator = False

# Locks and conditions for thread synchronization
gps_lock = Lock()
signature_lock = Lock()
record_lock = Lock()   
upload_lock = Lock()
capture_image_lock = Lock()
fingerprint_condition = Condition()
mid_video = False

# Variables to track media and user information
media_taken = 0
user_number = -1
camera_number_string = "2"
fingerprint = None  # Name of the user's fingerprint that opened the camera
fingerprint_mappings = {
    0: 'Dani Kasti',
    1: 'John Dale',
    2: 'Jace Christakis',
    3: 'Darius Paradie'
}

# Filepaths for saving videos and images
save_video_filepath = "/home/sdp/SDP-Camera/tmpVideos"
save_image_filepath = "/home/sdp/SDP-Camera/tmpImages"
object_count = None
gui_instance = None

# Initialize the camera settings
camera = cv2.VideoCapture(0)
camera.set(cv2.CAP_PROP_AUTOFOCUS, 0)
camera.set(cv2.CAP_PROP_FPS, 30.0)
camera.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc('m','j','p','g'))
camera.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc('M','J','P','G'))
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

# --------------------------------------------------------------------

def setup_gpio():
    """
    Sets up the GPIO pins for the mode and record buttons and assigns event detection callbacks.
    """
    global mode_button, record_button
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(record_button, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(mode_button, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    # Setup event detection for buttons
    GPIO.add_event_detect(mode_button, GPIO.FALLING, callback=toggle_image_mode, bouncetime=1000)
    GPIO.add_event_detect(record_button, GPIO.FALLING, callback=toggle_recording, bouncetime=3000)
    
# --------------------------------------------------------------------

def fingerprint_monitor():
    """
    Continuously monitors for fingerprint authentication and updates the `fingerprint` global variable.
    """
    global fingerprint, user_number
    while True:
        with fingerprint_condition:
            while fingerprint is not None:
                fingerprint_condition.wait()

            with record_lock:
                # Simulate fingerprint re-sign in
                print("Awaiting fingerprint...")
                while user_number < 0:  # Loop until a valid fingerprint is found
                    user_number = get_fingerprint(user_number)

                fingerprint = fingerprint_mappings[user_number]
                print("Fingerprint verified.")

# --------------------------------------------------------------------

def update_gps_data_continuously(gps_lock):
    """
    Continuously updates GPS data by reading it every 10 seconds and updating the global `gps_status` variable.
    """
    global gps_status
    while True:
        latitude, longitude, formatted_time, formatted_date = read_gps_data(gps_lock)
        gps_status = latitude != "None"
        time.sleep(10)  # Adjust the sleep time as needed based on how often you want to update GPS data

# --------------------------------------------------------------------

def update_wifi_status_continuously():
    """
    Continuously checks the WiFi status by pinging Google's DNS server and updates the global `wifi_status` variable.
    """
    global wifi_status
    while True:
        response = subprocess.run(['ping', '-c', '1', '8.8.8.8'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        wifi_status = response.returncode == 0
        print(f"\Twifi status in wifi thread: {wifi_status}")
        time.sleep(5)

# --------------------------------------------------------------------

class PhotoLockGUI(FloatLayout):
    """
    The main GUI class for the PhotoLock application.
    It handles the display of video, GPS, and WiFi status, as well as fingerprint verification.
    """
    def __init__(self, capture, **kwargs):
        super(PhotoLockGUI, self).__init__(**kwargs)

        # Start background threads for GPS data, WiFi status, media upload, and fingerprint monitoring
        Thread(target=update_gps_data_continuously, args=(gps_lock,), daemon=True).start()
        Thread(target=update_wifi_status_continuously, daemon=True).start() 
        Thread(target=upload_saved_media_continuously, args=(upload_lock,), daemon=True).start()
        Thread(target=fingerprint_monitor, daemon=True).start()

        Window.bind(on_key_down=self.on_key_down)

        self.capture = capture
        self.last_frame_texture = None  # To hold the texture of the last frame

        # Status images and labels
        self.wifi_status_image = Image(source='images/nowifi.png', size_hint=(None, None), size=(100, 45))
        self.gps_status_image = Image(source='images/nogps.png', size_hint=(None, None), size=(120, 54))
        self.status_layout = BoxLayout(size_hint=(None, None), size=(100, 45),
                                       pos_hint={'center_x': 0.5, 'center_y': 0.05})

        with self.status_layout.canvas.before:
            Color(0, 0, 0, 0.4)  # Semi-transparent black background
            self.rect = Rectangle(size=self.status_layout.size, pos=self.status_layout.pos)
            self.recording_color = Color(1, 0, 0, 0)  # Start with transparent (invisible)
            self.recording_indicator = Ellipse(size=(50, 50), pos=(740, 410))
            self.status_color = Color(0, 0, 0, 0.4)  # Semi-transparent black background
            self.status_background = Rectangle(size=(70, 120), pos=(25, 354))

        self.status_layout.bind(pos=self.update_rect, size=self.update_rect)
        
        self.img1 = Image(keep_ratio=False, allow_stretch=True)
        self.add_widget(self.img1)

        self.animation_overlay = FloatLayout(size_hint=(1, 1))
        self.fingerprint_label = Label(text='Scan Fingerprint', color=(1, 1, 1, 1), font_size='60sp', pos_hint={'center_x': 0.5, 'center_y': 0.5})
        self.animation_overlay.add_widget(self.fingerprint_label)

        # Fingerprint label and its background
        self.fingerprint_bg_color = Color(0, 0, 0, 0)  # Initially transparent
        self.fingerprint_bg_rect = Rectangle(size=(500, 100), pos=(150, 190))

        with self.canvas.before:
            self.canvas.add(self.fingerprint_bg_color)
            self.canvas.add(self.fingerprint_bg_rect)
            Color(0, 0, 0, 0.8)  # Semi-transparent black background

        self.add_widget(self.animation_overlay)
        self.bind(size=self.adjust_video_size)

        self.status_label = Label(text='Image', color=(1, 1, 1, 1), font_size='30sp')
        self.status_layout.add_widget(self.status_label)
        self.add_widget(self.status_layout)

        self.add_widget(self.wifi_status_image)
        self.bind(size=self.adjust_wifi_image_position)
        self.add_widget(self.gps_status_image)
        self.bind(size=self.adjust_gps_image_position)

        # Countdown label and its background
        self.bg_color = Color(0, 0, 0, 0)  # Initially transparent
        self.bg_rect = Rectangle()
        self.countdown_label = Label(text="", font_size='30sp', size_hint=(None, None),
                                     size=(100, 50), pos_hint={'center_x': 0.5, 'center_y': 0.5})

        with self.canvas.before:
            self.canvas.add(self.bg_color)
            self.canvas.add(self.bg_rect)
            Color(0, 0, 0, 0.4)  # Semi-transparent black background
            self.indicators_bg_rect = Rectangle(size=(150, 130), pos=(650, 350))
        
        self.add_widget(self.countdown_label)

        self.bind(size=self._update_bg_and_label_pos, pos=self._update_bg_and_label_pos)
        Clock.schedule_interval(self.update, 1.0 / 33.0)

        Clock.schedule_interval(self.check_wifi_status, 5)
        self.check_wifi_status(0)  # Immediately check the WiFi status upon start
        Clock.schedule_interval(self.check_gps_status, 10)
        self.check_gps_status(0)  # Immediately check the GPS status upon start

    def _update_bg_and_label_pos(self, *args):
        """
        Update the position of the countdown label and background rectangle.
        """
        self.bg_rect.pos = (self.width / 2 - 25, self.height / 2 - 25)
        self.bg_rect.size = (50, 50)
        self.countdown_label.pos = (self.width / 2 - 100, self.height / 2 - 50)

    def update(self, dt):
        """
        Update the video feed, status labels, and other visual elements on the GUI.
        """
        ret, frame = self.capture.read()

        if ret:
            self.last_frame = frame  # Store the last frame
            buf1 = cv2.flip(frame, 0)
            buf = buf1.tobytes()
            texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
            texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            self.img1.texture = texture
            self.last_frame_texture = texture  # Update the last frame's texture
            
            mode_text = "Image" if image_mode else "Video"
            self.status_label.text = f"{mode_text}"

            if user_number > -1:
                fingerprint_text = ""
            elif user_number == -1:
                fingerprint_text = "Scan Fingerprint"
            else:  # Handle cases where user_number < -1
                fingerprint_text = "Invalid Scan"

            self.fingerprint_bg_color.rgba = (0, 0, 0, .8) if not fingerprint else (0, 0, 0, 0)
            self.fingerprint_label.text = f"{fingerprint_text}"

            self.recording_color.a = 1 if recording_indicator else 0

    def check_wifi_status(self, dt):
        """
        Update the WiFi status icon based on the global `wifi_status` variable.
        """
        global wifi_status

        self.wifi_status_image.source = 'images/wifi.png' if wifi_status else 'images/nowifi.png'

    def adjust_wifi_image_position(self, instance, value):
        """
        Adjust the position of the WiFi status icon.
        """
        left_offset = 10  # Distance from the right edge
        top_offset = 10   # Distance from the top edge
        
        self.wifi_status_image.pos = (left_offset, 
                                    self.height - self.wifi_status_image.height - top_offset)

    def check_gps_status(self, dt):
        """
        Update the GPS status icon based on the global `gps_status` variable.
        """
        global gps_status
        self.gps_status_image.source = 'images/gps.png' if gps_status else 'images/nogps.png'

    def adjust_gps_image_position(self, instance, value):
        """
        Adjust the position of the GPS status icon.
        """
        left_offset = 0   # Distance from the left edge
        top_offset = 70   # Distance from the top edge
        
        self.gps_status_image.pos = (left_offset, 
                                    self.height - self.gps_status_image.height - top_offset)

    def adjust_video_size(self, *args):
        """
        Adjust the size and position of the video feed to maintain the correct aspect ratio.
        """
        video_aspect_ratio = 15.0 / 9.0  # Aspect ratio of the video feed
        window_width, window_height = self.size

        video_width = window_width
        video_height = video_width / video_aspect_ratio

        # Center the video in the window
        self.img1.size = (video_width, video_height)
        self.img1.pos = ((window_width - video_width) / 2, 0)

    def update_rect(self, instance, value):
        """
        Update the position and size of the background rectangle for status labels.
        """
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def start_countdown(self, duration=5):
        """
        Start a countdown timer with the specified duration (in seconds).
        """
        self.countdown = duration
        self.countdown_label.text = str(self.countdown)
        self.bg_color.rgba = (0, 0, 0, .4)  # Make the background visible
        Clock.schedule_interval(self.update_countdown, 1)

    def update_countdown(self, dt):
        """
        Update the countdown timer each second.
        """
        self.countdown -= 1
        if self.countdown > 0:
            self.countdown_label.text = str(self.countdown)
        else:
            self.end_countdown()

    def end_countdown(self):
        """
        End the countdown timer and hide the background.
        """
        self.countdown_label.text = ""
        self.bg_color.rgba = (0, 0, 0, 0)  # Make the background transparent again
        Clock.unschedule(self.update_countdown)

    def on_key_down(self, window, key, *args):
        """
        Handle key press events, specifically triggering animations on Enter key press.
        """
        if key == 13:  # Check if the pressed key is Enter (keycode == 13)
            self.animate_last_frame()
            
    def animate_last_frame(self):
        """
        Animate the last frame captured by the camera and display it on the GUI.
        """
        if self.last_frame_texture:
            animated_image = Image(texture=self.last_frame_texture, size_hint=(None, None), size=(800, 480),keep_ratio=False, allow_stretch=True)
            self.animation_overlay.add_widget(animated_image)

            animation = Animation(pos=(10, 10), size=(150, 90), duration=.3) + Animation(opacity=1, duration=6) + Animation(opacity=0, duration=.3)
            animation.bind(on_complete=lambda *x: self.animation_overlay.remove_widget(animated_image))
            animation.start(animated_image)

    def animate_upload(self):
        """
        Animate the upload process, displaying a label indicating the upload is in progress.
        """
        upload_label = Label(text="Uploading...", size_hint=(None, None), size=(200, 50),
                             pos=(self.width / 2 - 100, self.height - 60))  # Position it at the top

        # Add this label to the animation overlay
        self.animation_overlay.add_widget(upload_label)

        # Define the animation sequence: fade in, stay, fade out
        animation = Animation(opacity=1, duration=0.5) + \
                    Animation(opacity=1, duration=2) + \
                    Animation(opacity=0, duration=0.5)

        # Remove the label from the overlay once the animation is complete
        animation.bind(on_complete=lambda *x: self.animation_overlay.remove_widget(upload_label))

        # Start the animation
        animation.start(upload_label)

# --------------------------------------------------------------------

class PhotoLockApp(App):
    """
    The main application class for the PhotoLock system, managing the GUI and camera capture.
    """
    def build(self):
        global gui_instance

        self.capture = cv2.VideoCapture(2)
        self.capture.set(cv2.CAP_PROP_AUTOFOCUS, 0)
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.capture.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc('m','j','p','g'))
        self.capture.set(cv2.CAP_PROP_FPS, 30.0)
        
        gui_instance = PhotoLockGUI(self.capture)  # Assign the instance to the global variable
        return gui_instance

    def on_stop(self):
        """
        Release the camera resources when the application stops.
        """
        self.capture.release()

# --------------------------------------------------------------------

def gui_thread():
    """
    Start the Kivy GUI application in a separate thread.
    """
    PhotoLockApp().run()

# --------------------------------------------------------------------

def toggle_image_mode(channel):
    """
    Toggle between image and video modes based on button press.
    """
    global image_mode
    global recording_indicator
    global camera

    with record_lock:
        if not recording_indicator:
            image_mode = not image_mode
        
        if image_mode and camera is None and not recording_indicator:
            # Initialize the camera for image mode
            camera = cv2.VideoCapture(0)
            camera.set(cv2.CAP_PROP_AUTOFOCUS, 0)
            camera.set(cv2.CAP_PROP_FPS, 30.0)
            camera.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc('m','j','p','g'))
            camera.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc('M','J','P','G'))
            camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
            camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

        if not image_mode and camera is not None:
            # Release the camera for video mode
            camera.release()
            camera = None

# --------------------------------------------------------------------

def toggle_recording(channel): 
    """
    Start or stop video recording based on button press.
    """
    global mode_button
    global record_button
    global image_mode
    global ffmpeg_process
    global object_count
    global recording_indicator 
    global record_lock
    global mid_video
    global camera
    global gui_instance
    global media_taken
    global fingerprint
    global user_number

    if recording_indicator and not mid_video:
        return 
    
    if not fingerprint:
        return
    
    with record_lock:
        print("Acquired lock in toggle_recording()")
        if not image_mode and not mid_video:   # Video mode and not recording 
            object_count = count_files(save_video_filepath)
            recording_indicator = True
            ffmpeg_process = start_recording(object_count)
            mid_video = True
            print("Released lock after starting video in toggle_recording()")

        elif mid_video:  # Currently recording a video 
            print("In the elif for mid_video == True")
            # Stop recording the video
            recording_indicator = False
            Clock.schedule_once(lambda dt: gui_instance.animate_last_frame())
            ffmpeg_process = stop_recording(ffmpeg_process, object_count)
            media_taken += 1
            mid_video = False
            print("Released lock after stopping video in toggle_recording()")

        elif image_mode and not mid_video:  # Image mode, not recording video
            # Capture an image
            recording_indicator = True
            capture_image(camera, capture_image_lock)
            media_taken += 1
            recording_indicator = False
            print("Released lock after capturing image in toggle_recording()")

        else:
            print("Error: Unknown state in the else case of handle_capture()")
            quit()

        if media_taken > 3:
            with fingerprint_condition:
                user_number = -1
                fingerprint = None
                media_taken = 0
                fingerprint_condition.notify_all()

# --------------------------------------------------------------------

def start_recording(object_count):
    """
    Start recording video using FFmpeg and save it to the specified directory.
    """
    save_video_filepath = "/home/sdp/SDP-Camera/tmpVideos"  # Ensure this is defined or passed correctly

    # Ensure the directory exists
    if not os.path.exists(save_video_filepath):
        os.makedirs(save_video_filepath)  # Create the directory and any necessary parents

    video_filepath_raw = os.path.join(save_video_filepath, f'{object_count}raw.avi')

    command = [
        'ffmpeg',
        '-framerate', '30',
        '-video_size', '1920x1080',
        '-i', '/dev/video0',
        '-f', 'alsa', '-i', 'default',
        '-c:v', 'h264_v4l2m2m',
        '-pix_fmt', 'yuv420p',
        '-b:v', '4M',
        '-bufsize', '4M',
        '-c:a', 'aac',
        '-b:a', '128k',
        '-threads', '4',
        video_filepath_raw
    ]
    
    # Start FFmpeg process
    ffmpeg_process = subprocess.Popen(command, stdin=subprocess.PIPE)

    # Start countdown animation
    Clock.schedule_once(lambda dt: gui_instance.start_countdown(duration=3), 0)
    
    return ffmpeg_process

# --------------------------------------------------------------------

def stop_recording(ffmpeg_process, object_count):
    """
    Stop the video recording and save the final video file. This function does not upload the video.
    """
    ffmpeg_process.stdin.write(b'q\n')
    ffmpeg_process.stdin.flush()
    ffmpeg_process.wait()  # Wait for the process to terminate

    print("Stopped raw recording")

    video_filepath = os.path.join(save_video_filepath, f'{object_count}.avi')
    video_filepath_raw = os.path.join(save_video_filepath, f'{object_count}raw.avi')
    
    ffmpeg_cut_command = [
        'ffmpeg',
        '-i', video_filepath_raw,  # Input file path
        '-ss', '3',  # Start trimming 5 seconds into the video
        '-c:v', 'copy',  # Copy the video stream without re-encoding
        '-c:a', 'copy',  # Copy the audio stream without re-encoding
        '-threads', '4',
        video_filepath  # Output file path
    ]
    
    print("Began cutting recording")
    ffmpeg_cut_process = subprocess.Popen(ffmpeg_cut_command, stdin=subprocess.PIPE)
    ffmpeg_cut_process.wait()
    print("Stopped cutting recording")
    os.remove(video_filepath_raw)  # Remove the raw video file after processing

    # Start a thread to process and upload the video
    Thread(target=main, args=(fingerprint, video_filepath, camera_number_string, save_video_filepath, gps_lock, signature_lock, upload_lock,)).start()

    return None

# --------------------------------------------------------------------

def capture_image(camera, capture_image_lock):
    """
    Capture an image from the camera and process it for uploading.
    """
    print("Capture_image called")
    global gui_instance

    if not camera.isOpened():
        print("\tError: Camera not found or could not be opened.")
        return None

    with capture_image_lock:
        # Capture a single frame from the camera
        frame = None
        for i in range(35):
            ret, frame = camera.read()
        
        # Animate the captured image frame
        Clock.schedule_once(lambda dt: gui_instance.animate_last_frame())
        
        if ret:
            image = frame
            # Start automatic processing and upload process for images
            Thread(target=main, args=(fingerprint, image, camera_number_string, save_image_filepath, gps_lock, signature_lock, upload_lock,)).start()

        else:
            print("\tError: Failed to capture an image.")

# --------------------------------------------------------------------

def count_files(directory_path):
    """
    Helper function to return the number of AVI files in the specified directory.
    """
    if not os.path.exists(directory_path):
        print(f"Directory not found: {directory_path}")
        return 0

    count = 0
    for file_name in os.listdir(directory_path):
        if file_name.lower().endswith('.avi'):
            count += 1

    return count

# -------------------------------------------------------------------

def upload_saved_media_continuously(upload_lock):
    """
    Continuously attempts to upload saved media (images and videos) when WiFi is available.
    """
    global gui_instance
    while True:
        if wifi_status:  # Assuming wifi_status is a global variable indicating WiFi availability
            with upload_lock:  # Ensure exclusive access to the file system
                try:
                    for save_path in [save_image_filepath, save_video_filepath]:
                        files = os.listdir(save_path)
                        paired_files = find_paired_files(files)

                        for base_name in paired_files:
                            image_path = os.path.join(save_path, base_name + '.png')
                            video_path = os.path.join(save_path, base_name + '.avi')
                            metadata_path = os.path.join(save_path, base_name + '.json')

                            try:
                                if os.path.exists(image_path):
                                    Clock.schedule_once(lambda dt: gui_instance.animate_upload())
                                    upload_image_file(image_path, metadata_path)
                                elif os.path.exists(video_path):
                                    Clock.schedule_once(lambda dt: gui_instance.animate_upload())
                                    upload_video_file(video_path, metadata_path)
                            except Exception as e:
                                print(f"Error uploading file {base_name}: {e}")
                except Exception as e:
                    print(f"Unexpected error: {e}")
        
        time.sleep(10)  # Wait before trying again

# -------------------------------------------------------------------

def find_paired_files(files):
    """
    Extract base filenames that have both an image/video and a metadata file.
    """
    base_names = set()
    for file in files:
        if file.lower().endswith(('.png', '.avi', '.json')):
            base_names.add(file.rsplit('.', 1)[0])
    return {base for base in base_names if any(f"{base}.json" in files for f in ['png', 'avi'])}

# -------------------------------------------------------------------

def upload_image_file(image_path, metadata_path):
    """
    Upload an image file along with its metadata.
    """
    image = cv2.imread(image_path)
    _, encoded_image = cv2.imencode(".png", image)
    metadata = read_metadata(metadata_path)
    upload_image(encoded_image.tobytes(), metadata)
    os.remove(image_path)
    os.remove(metadata_path)

# -------------------------------------------------------------------

def upload_video_file(video_path, metadata_path):
    """
    Upload a video file along with its metadata.
    """
    with open(video_path, 'rb') as video:
        video_bytes = video.read()
    metadata = read_metadata(metadata_path)
    upload_video(video_bytes, metadata)
    os.remove(video_path)
    os.remove(metadata_path)

# -------------------------------------------------------------------
                            
def read_metadata(file_path_metadata):
    """
    Read metadata from the specified JSON file.
    """
    with open(file_path_metadata, 'r') as file:
        metadata = json.load(file)
        return metadata
    
# -------------------------------------------------------------------

if __name__ == '__main__':
    setup_gpio()
    gui_thread()  # Start the Kivy application
    GPIO.cleanup()  # Clean up GPIO resources
