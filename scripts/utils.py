import requests
import json
import time

# Function to get the sunrise and sunset time for a given location and date
# API Credits: https://sunrisesunset.io/ 

def get_sunrise_sunset(lat: str, lng: str, date: str, date_end: str = None, max_retries: int = 5):
    """
    Function to get the sunrise and sunset time for a given location and date, at the timezone of the location.
    Args:
        lat: Latitude of the location
        lng: Longitude of the location
        date: Date for which the sunrise and sunset time is to be calculated  (YYYY-MM-DD)
        date_end (optional): If provided, range of date from date to date_end will be used to calculate the sunrise and sunset time (YYYY-MM-DD) (Default: None)
        max_retries (optional): Maximum number of retries in case of a request failure (Default: 5)
    Returns:
        data: JSON response containing the sunrise and sunset time

    """
    url = f"https://api.sunrisesunset.io/json?lat={lat}&lng={lng}" 
    if date_end:
        url += f"&date_start={date}&date_end={date_end}"
    else:
        url += f"&date={date}"
    retries = 0
    while retries < max_retries:
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = json.loads(response.text)
            return data
        except requests.exceptions.RequestException as e:
            retries += 1
            if retries >= max_retries:
                return {"status": "error", "message": f"Failed to get sunrise and sunset time for {date} at {lat}, {lng} after {max_retries} retries."}
            time.sleep(0.1) # Sleep for 0.1 seconds before retrying

