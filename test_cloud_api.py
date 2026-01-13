import requests
import json

# Your REAL Cloud URL
CLOUD_URL = "https://skivqtfkjd63bazhdlci2jx7rq0htusv.lambda-url.us-east-2.on.aws/"

def test_cloud_get_clients():
    print(f"\n--- Testing REAL Cloud API ---")
    print(f"URL: {CLOUD_URL}")
    
    payload = {
        "operation": "get_clients"
    }
    
    try:
        response = requests.post(CLOUD_URL, json=payload)
        print(f"Status Code: {response.status_code}")
        print("Response Content:")
        print(json.dumps(response.json(), indent=4))
        
        if response.status_code == 200:
            print("\n✅ SUCCESS: Your React app can now use this URL!")
        else:
            print("\n❌ FAILED: Unexpected status code.")
            
    except Exception as e:
        print(f"\n[!] Error connecting to cloud: {e}")

if __name__ == "__main__":
    test_cloud_get_clients()
