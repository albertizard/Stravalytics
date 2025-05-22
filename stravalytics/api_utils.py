import requests
import urllib3

# Disable certificate verification warning. See https://urllib3.readthedocs.io/en/latest/advanced-usage.html#tls-warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class ApiUtils:
    """
    Simple API utils class that 
    """

    def api_call(self, method, url, **kwargs):
        """
        Handle API calls.
        examples of method are: "GET", "PUT"
        Returns the JSON response.
        """

        try:
            response = requests.request(method, url, **kwargs)
            # requests.get(url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as errh:
            print("HTTP error occurred:", errh)
        except requests.exceptions.ConnectionError as errc:
            print("Connection error occurred:", errc)
        except requests.exceptions.Timeout as errt:
            print("Timeout error occurred:", errt)
        except requests.exceptions.RequestException as err:
            print("An unexpected error occurred:", err)
        return None