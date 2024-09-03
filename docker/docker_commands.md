# Pushing built image to ECR for Lambda
# Tutorial Reference: https://docs.aws.amazon.com/lambda/latest/dg/python-image.html 

# Create a new ECR (Elastic Container Registry) repository in your AWS account
# Replace 'my-repo' with your desired repository name and 'my-region' with your AWS region
aws ecr create-repository --repository-name my-repo --region my-region

# Example command for creating an ECR repository named 'live' in the 'us-east-2' region
aws ecr create-repository --repository-name live --region us-east-2   

# Build a Docker image targeting the 'linux/amd64' platform with your chosen image name
# Replace '<any_image_name_you_want>' with your desired image name
docker build --platform linux/amd64 -t <any_image_name_you_want> . 

# Example command for building a Docker image named 'liveverify'
docker build --platform linux/amd64 -t liveverify .    

# Tag the Docker image with a destination path in ECR
# Replace '<any_image_name_you_want>', '<tag>', and '<destination>' with appropriate values
docker tag <any_image_name_you_want>:<tag> <destination>.us-east-2.amazonaws.com/<any_image_name_you_want>:<tag>

# Example command for tagging an image named 'live' with 'my-tag' in ECR
docker tag <tag> <destination>.amazonaws.com/live:my-tag    

# Push the Docker image to ECR
# Replace '359793706805.dkr.ecr.us-east-2.amazonaws.com/sdp:latest' with your own ECR path
docker push 359793706805.dkr.ecr.us-east-2.amazonaws.com/sdp:latest

# Example command for pushing an image tagged 'my-tag' to ECR
docker push 359793706805.dkr.ecr.us-east-2.amazonaws.com/live:my-tag    

# --------------------------------------------------
# ^^^^^^ The 'image name : tag' example

# Pushing changes to an Image if you want to update it 
# Rebuild the Docker image with the updated contents
docker build --platform linux/amd64 -t <tag> .

# Tag the updated image for pushing to ECR
docker tag <tag> <destination>.amazonaws.com/final:latest

# Push the updated image to ECR
docker push <destination>.amazonaws.com/final:latest

# Testing Local Deployment
# Run the Docker container locally on port 9000
# Replace '<any_image_name_you_want>:test' with your actual image name and tag
terminal: docker run -p 9000:8080 <any_image_name_you_want>:test  

# Test the locally running container using PowerShell
# Sends a POST request to the Lambda function's invocation endpoint
Windows Powershell:  Invoke-WebRequest -Uri "http://localhost:9000/2015-03-31/functions/function/invocations" -Method Post -Body '{}' -ContentType "application/json"
