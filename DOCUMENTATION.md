
# Project Documentation

## Table of Contents
- [Overview](#overview)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Installation](#installation)
- [Usage](#usage)
- [Scripts](#scripts)
- [Docker](#docker)
- [SpecialUse](#specialuse)
- [License](#license)

## Overview
This project contains various scripts and utilities for handling tasks such as GPS data parsing, video processing, image handling, and fingerprint recognition. The repository includes both Python scripts and Docker configuration files.

## Project Structure

\`\`\`plaintext
.
├── docker/
│   ├── docker_commands.txt
│   ├── Dockerfile
│   ├── lambda_function.py
│   ├── lambda_function.sh
│   ├── requirements.txt
│   └── test_read_avi.py
├── specialUse/
├── .gitignore
├── check_wifi.py
├── create_combined_byte.py
├── create_digest.py
├── create_image.py
├── create_metadata.py
├── create_signature.py
├── create_video.py
├── DOCUMENTATION.md
├── get_fingerprint.py
├── GPS_uart.py
├── main_live_view.py
├── main.py
├── save_image.py
├── save_metadata.py
├── startup.sh
├── upload_image.py
├── upload_saved_image.py
├── upload_saved_video.py
└── upload_video.py
\`\`\`

### Docker
- **docker_commands.txt:** Contains useful Docker commands for managing containers and images related to this project.
- **Dockerfile:** The Dockerfile used to build the Docker image for this project.
- **lambda_function.py:** A Python script designed to be used as an AWS Lambda function.
- **lambda_function.sh:** A shell script related to the Lambda function.
- **requirements.txt:** Lists Python dependencies required for the Lambda function or Docker container.
- **test_read_avi.py:** A script to test reading AVI files, likely used in conjunction with Docker.

### SpecialUse
- Placeholder for special-use scripts or configurations.

### Python Scripts
- **check_wifi.py:** Script for checking the status of Wi-Fi connectivity.
- **create_combined_byte.py:** Script to create a combined byte object from various data (e.g., fingerprint, camera number).
- **create_digest.py:** Generates a SHA-256 digest from a combined byte object.
- **create_image.py:** Captures an image using OpenCV and saves it as a file.
- **create_metadata.py:** Creates metadata for a file, including a fingerprint, date, time, location, etc.
- **create_signature.py:** Generates a signature using a Trusted Platform Module (TPM).
- **create_video.py:** Captures video data, saves it to a file, and processes the video as bytes.
- **get_fingerprint.py:** Retrieves a fingerprint from a sensor using the PyFingerprint library.
- **GPS_uart.py:** Parses GPS data via UART and extracts latitude, longitude, and time information.
- **main_live_view.py:** Possibly handles a live video feed or other main application functionality.
- **main.py:** The main entry point of the application. This script might combine various modules and manage the flow of the application.
- **save_image.py:** Handles saving image data, possibly after processing or capturing.
- **save_metadata.py:** Saves metadata associated with an image or video file.
- **startup.sh:** A shell script for setting up or initializing the application, likely on a Raspberry Pi or similar device.
- **upload_image.py:** Handles uploading image files to a server or cloud storage.
- **upload_saved_image.py:** Uploads previously saved image files.
- **upload_saved_video.py:** Uploads previously saved video files.
- **upload_video.py:** Handles uploading video files.

### DOCUMENTATION.md
This is the current documentation file that you're reading.

## Getting Started
To get started with this project, clone the repository and follow the installation instructions below.

## Installation
1. **Clone the repository:**
   \`\`\`bash
   git clone https://github.com/your-repository-url.git
   cd your-repository
   \`\`\`

2. **Install dependencies:**
   If you're using the Docker setup, the dependencies will be managed within the Docker container. If not, install Python dependencies manually:
   \`\`\`bash
   pip install -r requirements.txt
   \`\`\`

3. **Set up the environment:**
   You will need to configure environment variables or update configuration files on your Raspberry Pi

