import base64

'''
File for encoding PEM public key content to Base64 format; that way we can store the key inside of a SQL database as a string
'''
# Specify the file path of your PEM file containing the public key
file_path = 'public.pem'

# Read the PEM file in binary mode
with open(file_path, 'rb') as file:
    binary_content = file.read()

# Encode the binary data to a Base64 string for easy storage and handling
encoded_content = base64.b64encode(binary_content).decode('utf-8')

# Print the Base64-encoded public key
print(encoded_content)
