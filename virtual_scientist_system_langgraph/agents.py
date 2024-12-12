import os
import requests
from dotenv import load_dotenv

load_dotenv()

class DuckDuckGoAgent:
    def __init__(self):
        self.name = "DuckDuckGo Agent"

    async def query(self, topic):
        try:
            # Perform the query using DuckDuckGo API
            response = requests.get(f"https://api.duckduckgo.com/?q={topic}&format=json")
            response.raise_for_status()  # Raise error for unsuccessful responses
            
            # Print the full response for debugging
            print("Full API Response:", response.json())  # Debugging line
            
            # Return the abstract (summary) of the topic from DuckDuckGo results
            return response.json().get('Abstract', 'No result found')
        except requests.exceptions.RequestException as e:
            return f"Error querying DuckDuckGo: {str(e)}"