import requests
import json

DATA_BASEURL='http://localhost:5116'

def fetch_data_from_api(endpoint):
    url = DATA_BASEURL+endpoint    
    response = requests.get(url)
    if response.status_code == 200:
        d= response.json()        
        return json.dumps(d)
    else:
        print(f"Failed to fetch content from URL. Status code: {response.status_code}")