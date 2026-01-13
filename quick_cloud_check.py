import requests
url = "https://gpdzr1oo65.execute-api.us-east-2.amazonaws.com/clients"
try:
    r = requests.get(url)
    print(f"Status: {r.status_code}")
    print(f"Data: {r.text[:200]}")
except Exception as e:
    print(f"Error: {e}")
