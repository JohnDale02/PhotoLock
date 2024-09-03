import hashlib

def create_digest(combined_data: bytes) -> bytes:
    """
    Creates a SHA-256 digest from the given combined data.

    This function takes in a byte object (combined data), creates a SHA-256 hash object,
    updates it with the combined data, and then returns the resulting digest.

    Args:
        combined_data (bytes): The byte object containing combined data to hash.

    Returns:
        bytes: The resulting SHA-256 digest of the input data.
    """

    # Create a new SHA-256 hash object
    sha256_hash = hashlib.sha256()
    
    # Update the hash object with the combined data
    sha256_hash.update(combined_data)

    # Return the digest (hashed value)
    return sha256_hash.digest()
