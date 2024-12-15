import os
import requests
from dotenv import load_dotenv

load_dotenv()

class DuckDuckGoAgent:
    def __init__(self):
        self.name = "DuckDuckGo Agent"

    async def query(self, topic):
        try:
            response = requests.get(f"https://api.duckduckgo.com/?q={topic}&format=json")
            response.raise_for_status()  
            
            print("Full API Response:", response.json())  
            
            return response.json().get('Abstract', 'No result found')
        except requests.exceptions.RequestException as e:
            return f"Error querying DuckDuckGo: {str(e)}"