#!/bin/bash

# This script serves as the startup script for the Raspberry Pi to launch the live camera view application.

# Set the DISPLAY environment variable to use the default display
export DISPLAY=:0

# Activate the Python virtual environment for the SDP project
source /home/sdp/sdpenv/bin/activate

# Grant full read/write/execute permissions to the /tmp directory (temporary files)
sudo chmod 777 /tmp

# Run the main live view Python script and redirect both stdout and stderr to a log file
python3 /home/sdp/SDP-Camera/main_live_view.py > /home/sdp/app.log 2>&1
