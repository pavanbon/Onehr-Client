import requests

url = "https://gpdzr1oo65.execute-api.us-east-2.amazonaws.com/docs"
try:
    response = requests.get(url)
    print(f"Status Code: {response.status_code}")
    print(f"Title: {response.text.split('<title>')[1].split('</title>')[0]}")
    print(f"Body snippet: {response.text[:200]}")
except Exception as e:
    print(f"Error: {e}")
