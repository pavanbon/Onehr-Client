import requests
import json

BASE_URL = "https://gpdzr1oo65.execute-api.us-east-2.amazonaws.com"

def verify_cloud_api():
    print(f"\n--- Verifying Cloud API at {BASE_URL} ---")
    
    # 1. Test GET /clients (Should now work WITHOUT token)
    try:
        url = f"{BASE_URL}/clients"
        print(f"Testing GET {url}...")
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ SUCCESS: The API is LIVE and NO LONGER needs a token.")
            data = response.json()
            print(f"Total Clients found: {len(data.get('clients', []))}")
            return True
        elif response.status_code == 401:
            print("❌ 401: Auth is still active. Please ensure you uploaded 'OneHR_API_Fixed_Final_v2.zip'.")
        else:
            print(f"❌ Failed: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    return False

if __name__ == "__main__":
    verify_cloud_api()
