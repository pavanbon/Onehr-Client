import requests
import json

# User provided URL was .../docs, so base is .../
# If they are using a Stage, it might be in the path, but let's assume the provided URL was the exact path to docs.
# We want to hit /clients
BASE_URL = "https://gpdzr1oo65.execute-api.us-east-2.amazonaws.com"

# The user might have a stage, e.g. /dev or /prod. 
# Usually 'Mangum' on Lambda uses the event path. 
# If the user accessed /docs directly, maybe configured at root? 
# Let's try to hit /clients directly.

def test_clients_no_auth():
    url = f"{BASE_URL}/clients"
    print(f"--- Testing {url} (No Auth) ---")
    
    try:
        response = requests.get(url)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ SUCCESS: API accepted request without token!")
            data = response.json()
            clients = data.get('clients', [])
            print(f"Found {len(clients)} clients.")
            if clients:
                print(f"First client: {clients[0].get('legalName')}")
        elif response.status_code == 403:
            print("❌ 403 Forbidden - Auth might still be required or WAF blocking.")
        elif response.status_code == 401:
            print("❌ 401 Unauthorized - Auth is definitely still required.")
        else:
            print(f"❌ Failed: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_clients_no_auth()
