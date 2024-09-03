import requests

def is_internet_available():
    """
    Check if the internet is available by sending an HTTP GET request to a reliable server.

    Returns:
        bool: True if the internet is available (status code 200), False otherwise.
    """
    try:
        # Send a simple HTTP GET request to Google
        response = requests.get("https://www.google.com", timeout=5)
        # Return True if the request is successful (HTTP 200)
        return response.status_code == 200
    except requests.ConnectionError:
        # Return False if there is a connection error (e.g., no internet)
        return False


def is_internet_availableTwo():
    """
    Check if the internet is available by sending an HTTP GET request to a reliable server.

    Returns:
        bool: True if the internet is available (status code 200), False otherwise.
    """
    try:
        # Send a simple HTTP GET request to Google
        response = requests.get("https://www.google.com", timeout=5)
        # Return True if the request is successful (HTTP 200)
        return response.status_code == 200
    except requests.ConnectionError:
        # Return False if there is a connection error (e.g., no internet)
        return False
