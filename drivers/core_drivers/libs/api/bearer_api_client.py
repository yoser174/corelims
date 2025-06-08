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

from datetime import datetime
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
        url = f"instruments/?instrument_id={instrument_id}"
        logging.debug("Fetching instrument data for ID: %s", instrument_id)
        return self.get(url)

    def get_all_instruments(self):
        """Fetches data for all instruments."""
        url = "instruments/"
        logging.debug("Fetching all instruments data.")
        return self.get(url)

    def get_instrument_tests(self, instrument_id: str, test_code: str):
        """Fetches instrument tests for a specific order ID and test code."""
        url = f"instrument_tests/?instrument_id={instrument_id}&test_code={test_code}"
        logging.debug(
            "Fetching instrument tests for instrument_id: %s, test_code: %s",
            instrument_id,
            test_code,
        )
        return self.get(url)

    def get_order_samples(self, sample_no: str):
        """Fetches order samples for a specific sample number."""
        url = f"order_samples/?sample_no={sample_no}"
        logging.debug("Fetching order samples for sample_no: %s", sample_no)
        return self.get(url)

    def get_order_results(self, order_id: str, test_id: str):
        """Fetches order results for a specific sample number."""
        url = f"order_results/?order_id={order_id}&test_id={test_id}"
        logging.debug(
            "Fetching order results for order_id: %s test_id: %s", order_id, test_id
        )
        return self.get(url)

    def get_test(self, test_id: str):
        """Fetches a specific test by its ID."""
        url = f"tests/?{test_id}"
        logging.debug("Fetching test data for test_id: %s", test_id)
        return self.get(url)

    def insert_result(
        self,
        sample_no,
        test_code,
        test_result,
        test_ref,
        test_unit,
        test_flag,
        instrument_id,
    ):
        # get instrument data
        instrument_data = self.get_instrument_data(instrument_id=instrument_id)
        if not instrument_data:
            logging.error(
                "No instrument data found for instrument_id: %s", instrument_id
            )
            return None
        instrument_name = instrument_data[0].get("name")
        """Inserts a result for a specific sample."""
        # get orders from sample_no
        get_order_samples = self.get_order_samples(sample_no=sample_no)
        if not get_order_samples:
            logging.error("No order samples found for sample_no: %s", sample_no)
            return None
        if not get_order_samples[0].get("order"):
            logging.error("Order ID not found for sample_no: %s", sample_no)
            return None
        # Assuming the first order sample is the one we want
        logging.debug("Order samples fetched: %s", get_order_samples)
        logging.info("Order samples for sample_no %s: %s", sample_no, get_order_samples)
        # Get the first order ID
        order_id = get_order_samples[0].get("order")

        # get test from test_code
        test = self.get_instrument_tests(
            instrument_id=instrument_id, test_code=test_code
        )
        if not test:
            logging.error(
                "No tests found for instrument_id: %s, test_code: %s",
                instrument_id,
                test_code,
            )
            return None
        if not test[0].get("test"):
            logging.error(
                "Test ID not found for instrument_id: %s, test_code: %s",
                instrument_id,
                test_code,
            )
            return None
        logging.debug("Tests fetched: %s", test)
        logging.info(
            "Tests for order_id %s, test_code %s: %s", order_id, test_code, test
        )
        # Assuming the first test is the one we want
        test_id = test[0]["test"]

        test_data = self.get_test(test_id=test_id)
        if not test_data:
            logging.error("No test data found for test_id: %s", test_id)
            return None
        if not test_data[0].get("id"):
            logging.error("Test ID not found in test data for test_id: %s", test_id)
            return None
        logging.debug("Test data fetched: %s", test_data)
        logging.info("Test data for test_id %s: %s", test_id, test_data)
        # Assuming the first test data is the one we want
        test_name = test_data[0].get("name")

        logging.debug("Order ID for sample_no %s: %s", sample_no, order_id)
        url = f"{self.api_url}results/"

        alfa_result = None
        numeric_result = None

        if test_result.isdigit():
            numeric_result = test_result
            logging.debug("Numeric result detected: %s", numeric_result)
        elif isinstance(test_result, str):
            alfa_result = test_result
            logging.debug("Alphanumeric result detected: %s", alfa_result)
        else:
            logging.error(
                "Invalid test result type for sample_no %s: %s",
                sample_no,
                type(test_result),
            )
            return None

        data = {
            "order": order_id,
            "test": test_id,
            "sample_no": sample_no,
            "numeric_result": numeric_result,
            "alfa_result": alfa_result,
            "test_code": test_code,
            "test_result": test_result,
            "test_ref": test_ref,
            "test_unit": test_unit,
            "test_flag": test_flag,
            "instrument_id": instrument_id,
        }
        logging.debug("Inserting result: %s", data)
        response = requests.post(url, json=data, headers=self.get_headers(), timeout=10)
        if response.status_code != 201:
            logging.error(
                "Failed to insert result with status code %s: %s",
                response.status_code,
                response.text,
            )
            response.raise_for_status()
            return False
        result = response.json()
        logging.debug("Result inserted successfully: %s", result)
        result_id = result.get("id")
        # update order_results
        order_result = self.get_order_results(order_id=order_id, test_id=test_id)
        if not order_result:
            logging.error(
                "No order results found for order_id: %s, test_id: %s",
                order_id,
                test_id,
            )
            return None
        logging.debug("Order results fetched: %s", order_result)
        logging.info(
            "Order results for order_id %s, test_id %s: %s",
            order_id,
            test_id,
            order_result,
        )
        # Assuming the first order result is the one we want
        order_result_id = order_result[0].get("id")
        if not order_result_id:
            logging.error(
                "Order result ID not found for order_id: %s, test_id: %s",
                order_id,
                test_id,
            )
            return None
        order_result[0]["result"] = result_id
        # post the updated order result
        update_url = f"{self.api_url}order_results/{order_result_id}/"
        logging.debug("Updating order result with ID: %s", order_result_id)
        update_response = requests.put(
            update_url, json=order_result[0], headers=self.get_headers(), timeout=10
        )
        if update_response.status_code != 200:
            logging.error(
                "Failed to update order result with status code %s: %s",
                update_response.status_code,
                update_response.text,
            )
            update_response.raise_for_status()
            return False
        logging.info("Order result updated successfully: %s", update_response.json())
        logging.debug("Order result updated successfully: %s", update_response.json())
        logging.info(
            "Result inserted and order result updated successfully for sample_no %s",
            sample_no,
        )
        logging.info(
            "Result inserted successfully for sample_no %s, order_id %s, test_id %s",
            sample_no,
            order_id,
            test_id,
        )
        # post history order
        history_url = f"{self.api_url}history_orders/"
        history_data = {
            "action_code": "RESENTRY",
            "action_user": "system",
            "action_date": datetime.now().isoformat(),
            "action_text": f"Result {test_result} inserted for analyt ({test_id}) {test_name} by instrument ({instrument_name})",
            "order": order_id,
            "test": test_id,
        }
        # post history order
        logging.debug("Posting history order with data: %s", history_data)
        history_response = requests.post(
            history_url, json=history_data, headers=self.get_headers(), timeout=10
        )
        if history_response.status_code != 201:
            logging.error(
                "Failed to post history order with status code %s: %s",
                history_response.status_code,
                history_response.text,
            )
            history_response.raise_for_status()
            return False
        return history_response.json()
