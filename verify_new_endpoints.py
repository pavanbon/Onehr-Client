import requests
import json

url = "https://gpdzr1oo65.execute-api.us-east-2.amazonaws.com/openapi.json"
try:
    response = requests.get(url)
    data = response.json()
    paths = list(data.get('paths', {}).keys())
    print("New Endpoints Found:")
    for p in sorted(paths):
        if 'advanced' in p or 'contract' in p or 'purchase' in p or 'requirement' in p or 'portal' in p:
            print(f"- {p}")
except Exception as e:
    print(f"Error: {e}")
