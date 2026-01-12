import requests
from typing import Optional
from app.config import FLIGHT_TOKEN_URL,FLIGHT_ATK_TOKEN


def get_easemytrip_token() -> Optional[str]:
    """
    Fetches the ITK token from EaseMyTrip API.

    Returns:
        str: The ITK token if successful, None otherwise.
    """

    headers = {
        "ATK": FLIGHT_ATK_TOKEN,
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(FLIGHT_TOKEN_URL, headers=headers, json={})
        response.raise_for_status()  # Raise an exception for bad status codes

        data = response.json()
        itk_token = data.get("ITK")

        if itk_token:
            return itk_token
        else:
            print("Warning: ITK field not found in response")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Error fetching token: {e}")
        return None
    except ValueError as e:
        print(f"Error parsing JSON response: {e}")
        return None


if __name__ == "__main__":
    # Example usage
    token = get_easemytrip_token()
    if token:
        print(f"Token retrieved: {token}")
    else:
        print("Failed to retrieve token")