import serial
from datetime import datetime, timedelta
import time 

def parse_nmea_sentence(sentence):
    """
    Parse a GNGGA NMEA sentence to extract latitude, longitude, and formatted time.

    Args:
        sentence (str): The NMEA sentence to parse.

    Returns:
        tuple: A tuple containing the parsed latitude, longitude, formatted time, and date.
               If the sentence is invalid, returns (None, None, None, None).
    """
    parts = sentence.split(',')

    # Check if the sentence is a GNGGA sentence
    if parts[0] in ['$GNGGA']:
        # Check if the data is valid based on the NMEA sentence
        if parts[0] == '$GNGGA' and parts[6] != '0':
            valid = True
        elif parts[0] == '$GNRMC' and parts[2] == 'A':
            valid = True
        else:
            valid = False

        if valid:
            time_value = parts[1]

            # Convert the time from the NMEA sentence to a datetime object
            nmea_time_str = time_value
            time_object = datetime.strptime(nmea_time_str, "%H%M%S.%f")

            # Adjust the time by subtracting 5 hours (assuming the time zone difference)
            new_time_object = time_object - timedelta(hours=5)

            # Format the adjusted time as a string
            formatted_time = new_time_object.strftime("%H:%M:%S")

            # Parse latitude information
            lat_value = float(parts[2])
            lat_hemisphere = parts[3]
            lat_degrees = int(lat_value / 100)
            lat_minutes = lat_value - (lat_degrees * 100)
            latitude = lat_degrees + (lat_minutes / 60)
            if lat_hemisphere == 'S':
                latitude *= -1  # Adjust for southern hemisphere

            # Parse longitude information
            lon_value = float(parts[4])
            lon_hemisphere = parts[5]
            lon_degrees = int(lon_value / 100)
            lon_minutes = lon_value - (lon_degrees * 100)
            longitude = lon_degrees + (lon_minutes / 60)
            if lon_hemisphere == 'W':
                longitude *= -1  # Adjust for western hemisphere

            # Get the current date
            now = datetime.now()
            formatted_date = now.strftime("%Y-%m-%d")

            # Return the parsed latitude, longitude, time, and date
            return latitude, longitude, formatted_time, formatted_date

    # Return None if the sentence is not valid or not a GNGGA sentence
    return None, None, None, None


def read_gps_data(gps_lock):
    """
    Read GPS data from a serial port and parse it to obtain latitude, longitude, time, and date.

    Args:
        gps_lock (threading.Lock): A lock to synchronize access to the GPS data.

    Returns:
        tuple: A tuple containing the latitude, longitude, formatted time, and date.
               Returns ("None", "None", "None", "None") if no valid data is received.
    """
    with gps_lock:
        # Open the serial port to read GPS data
        ser = serial.Serial('/dev/ttyS0', 9600, timeout=1)
        try: 
            start_time = time.time()
            while True:
                # Read a line from the serial port
                sentence = ser.readline().decode('utf-8', errors='ignore').strip()

                if sentence:
                    # Parse the NMEA sentence
                    latitude, longitude, formatted_time, formatted_date = parse_nmea_sentence(sentence)
                    
                    # If valid data is obtained, return it
                    if latitude is not None and longitude is not None and formatted_time is not None:
                        return latitude, longitude, formatted_time, formatted_date
                
                # Check if the timeout has been reached
                if time.time() - start_time > ser.timeout:
                    print("Timeout reached. No GPS data received.")
                    break
        except KeyboardInterrupt:
            print("Program terminated!")
        finally:
            # Close the serial port
            ser.close()
    
    # Return default values if no valid data is received
    return "None", "None", "None", "None"
