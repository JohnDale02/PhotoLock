import subprocess
import tempfile
import os
import base64

def create_signature(digest: bytes, signature_lock) -> str:
    """
    Generates a signature from a given digest using a Trusted Platform Module (TPM) and returns it as a base64 string.

    This function writes the provided digest to a temporary file, signs it using a TPM, and then
    reads the generated signature from a temporary file. The signature is encoded in base64 format
    and returned as a string. Temporary files are securely deleted after use.

    Args:
        digest (bytes): The SHA-256 digest that needs to be signed.
        signature_lock (threading.Lock): A lock to synchronize access to the TPM during the signing process.

    Returns:
        str: The generated signature encoded as a base64 string.

    Raises:
        Exception: If there is an error during the signature generation process.
    """
    with signature_lock:
        # Write the digest to a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as temp_digest_file:
            temp_digest_file.write(digest)
            digest_file = temp_digest_file.name

        # Create a temporary file to store the signature
        with tempfile.NamedTemporaryFile(delete=False) as temp_signature_file:
            signature_file = temp_signature_file.name

        # Command to sign the digest using the TPM
        tpm2_sign_command = [
            "sudo",
            "tpm2",
            "sign",
            "-Q",  # Quiet mode to suppress non-error messages
            "-c", "0x81010001",  # TPM key handle
            "-g", "sha256",  # Hash algorithm
            "-d", digest_file,  # Input digest file
            "-f", "plain",  # Output format
            "-s", "rsassa",  # Signature scheme
            "-o", signature_file  # Output signature file
        ]

        # Execute the TPM sign command
        result = subprocess.run(tpm2_sign_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8")

        # Delete the temporary digest file
        os.remove(digest_file)

        # Read the generated signature from the temporary file and delete the file
        signature = None
        if os.path.exists(signature_file):
            with open(signature_file, 'rb') as file:
                signature = file.read()
            os.remove(signature_file)

        # If the signature is successfully generated, encode it in base64 and return it
        if result.returncode == 0 and signature:
            signature_string = base64.b64encode(signature).decode('utf-8')
            return signature_string
        else:
            # Raise an exception if there is an error in generating the signature
            raise Exception("Error in generating signature: " + result.stderr)
