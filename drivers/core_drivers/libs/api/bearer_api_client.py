"""
BearerApiClient is a class that provides methods to interact with an API using Bearer token authentication.
It allows you to set the token and make GET requests to the API.
Args:
    token (str): The Bearer token used for authentication.
Methods:
    get_headers(): Returns the headers required for the API request, including the Bearer token.
    get(url: str): Makes a GET request to the specified URL with the Bearer token in the headers and returns the JSON response.
def __init__(self, token: str):
"""

import logging

import requests


class BearerApiClient:
    """BearerApiClient is a class that provides methods to interact with an API using Bearer token authentication.
    It allows you to set the token and make GET requests to the API.
    Args:
        token (str): The Bearer token used for authentication.
        api_url (str): The base URL of the API. Defaults to "http://localhost:8000/api/".
    Methods:
        get_headers(): Returns the headers required for the API request, including the Bearer token.
        get(url: str): Makes a GET request to the specified URL with the Bearer token in the headers and returns the JSON response.
    """

    def __init__(self, token: str, api_url: str = "http://localhost:8000/api/"):
        self.token = token
        self.api_url = api_url
        logging.info(
            "BearerApiClient initialized with token: %s and API URL: %s",
            self.token,
            self.api_url,
        )

    def get_headers(self):
        """Returns the headers required for the API request, including the Bearer token."""
        if not self.token:
            logging.error("No Bearer token provided.")
            raise ValueError("Bearer token is required for authentication.")
        logging.debug("Generating headers with Bearer token.")
        logging.info("Using Bearer token: %s", self.token)
        # Return the headers with the Bearer token
        return {"Authorization": f"Bearer {self.token}"}

    def get(self, url: str):
        """Makes a GET request to the specified URL with the Bearer token in the headers and returns the JSON response."""
        logging.debug("Making GET request to URL: %s", url)
        if not url.endswith("/"):
            url += "/"
        url = self.api_url + url.lstrip("/")  # Ensure the URL is absolute
        headers = self.get_headers()
        response = requests.get(url, headers=headers, timeout=10)
        logging.debug("GET request to %s with headers: %s", url, headers)
        if response.status_code != 200:
            logging.error(
                "GET request failed with status code %s: %s",
                response.status_code,
                response.text,
            )
            response.raise_for_status()
        else:
            logging.info("GET request successful: %s", response.json())
        return response.json()

    def get_instrument_data(self, instrument_id: str):
        """Fetches data for a specific instrument by its ID."""
        url = f"{self.api_url}instruments/{instrument_id}/"
        logging.debug("Fetching instrument data for ID: %s", instrument_id)
        return self.get(url)

    def get_all_instruments(self):
        """Fetches data for all instruments."""
        url = f"instruments/"
        logging.debug("Fetching all instruments data.")
        return self.get(url)
