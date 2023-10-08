import requests
import json


class APITask():


    def __init__(self, id: None):

        self.jsonReturn = {}
        # Define the API URL
        self.id = id
        api_url = f"http://localhost:3000/matches{self.id}"

       
        # Define the query parameter
        query_parameter = {"token": "k0"}

        # Define the header parameter
        header_parameter = {"procon-token": "k"}

        # Make the API request
        response = requests.get(api_url, params=query_parameter, headers=header_parameter)

        # Check if the request was successful
        if response.status_code == 200:

            # Print the response data
            print(response.json())
            self.jsonReturn= response.json()
            
           

        else:

            # Print the error message
            print(f"API request failed: {response.status_code}")

    def postAction():

        # Define the JSON data to send
        json_data = {
        [{'turn': 1, 'actions': [{'type': 0, 'dir': 0}]}]
        }

        # Set the request headers
        headers = {
        "Content-Type": "application/json"
        }

        # Make the POST request
        response = requests.post(
        "https://example.com/api/users",
        headers=headers,
        json=json_data
        )

        # Check the response status code
        if response.status_code == 200:
        # Success!
            print("JSON data sent successfully")
        else:
        # Error!
            print("Error sending JSON data:", response.status_code)

    