import requests

url = "https://gpdzr1oo65.execute-api.us-east-2.amazonaws.com/"
try:
    response = requests.get(url)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")
