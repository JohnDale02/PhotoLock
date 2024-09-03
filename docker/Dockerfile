# Use the official AWS Lambda Python 3.11 base image
# This image is provided by AWS and includes the necessary runtime for Lambda functions
FROM public.ecr.aws/lambda/python:3.11

# Install FFmpeg
# FFmpeg is a multimedia framework used for processing audio, video, and other multimedia files and streams
# The following commands install FFmpeg from a static build:
RUN yum install -y tar gzip xz && \
    curl -o ffmpeg.tar.gz https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz && \
    tar -xvf ffmpeg.tar.gz && \
    mv ffmpeg-*-amd64-static/ffmpeg /usr/local/bin/ && \
    mv ffmpeg-*-amd64-static/ffprobe /usr/local/bin/ && \
    rm -rf ffmpeg*.tar.gz ffmpeg-*-amd64-static

# Copy the requirements.txt file to the Lambda task root directory
# The requirements.txt file lists all Python dependencies for the Lambda function
COPY requirements.txt ${LAMBDA_TASK_ROOT}

# Install Python packages specified in requirements.txt
RUN pip install -r requirements.txt

# Copy the Lambda function code to the Lambda task root directory
# This code contains the logic for your Lambda function
COPY lambda_function.py ${LAMBDA_TASK_ROOT}

# Set the CMD (Command) to the Lambda function handler
# This tells the Lambda runtime which function to execute when the Lambda function is invoked
CMD [ "lambda_function.handler" ]
