def print_first_last_bytes_of_avi(filepath):
    """
    Prints the first and last 10 bytes of an AVI file in hexadecimal format.

    Args:
        filepath (str): The path to the AVI file.

    Raises:
        FileNotFoundError: If the specified file does not exist.
        Exception: For any other unexpected errors.
    """
    try:
        with open(filepath, 'rb') as file:
            # Read the entire file into a bytes object
            data = file.read()
            
            # Get the first 10 and last 10 bytes of the file
            first_10_bytes = data[:10]
            last_10_bytes = data[-10:]
            
            # Print the first and last 10 bytes in hexadecimal format
            print("First 10 bytes (hex):", first_10_bytes.hex())
            print("Last 10 bytes (hex):", last_10_bytes.hex())

    except FileNotFoundError:
        print(f"File not found: {filepath}")
    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage
print_first_last_bytes_of_avi('C:\\Users\\John Dale\\Downloads\\7.avi')
