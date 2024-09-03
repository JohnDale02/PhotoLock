from PIL import Image, ImageDraw
import os

def add_line_to_image(image_path, output_directory):
    # Ensure the output directory exists
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Open the image
    with Image.open(image_path) as img:
        # Create a drawing context
        draw = ImageDraw.Draw(img)
        
        # Calculate line coordinates (from top left to bottom right)
        start = (0, 0)
        end = (img.width, img.height)
        
        # Draw the line
        draw.line([start, end], fill="black", width=10)
        
        # Construct the output path
        basename = os.path.basename(image_path)
        output_path = os.path.join(output_directory, basename)
        
        # Save the modified image
        img.save(output_path)
        print(f"Saved modified image to {output_path}")

def process_all_png_files(input_directory, output_directory):
    # List all PNG files in the input directory
    for filename in os.listdir(input_directory):
        if filename.endswith('.png'):
            # Construct the full path to the file
            file_path = os.path.join(input_directory, filename)
            
            # Add line to the image and save to the output directory
            add_line_to_image(file_path, output_directory)

# Directories where your PNG files are stored and where to save the modified files
input_directory = "C:\\S3Backup"
output_directory = "C:\\S3BackupModified"

# Process all PNG files in the directory
process_all_png_files(input_directory, output_directory)
