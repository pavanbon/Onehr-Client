import requests
import json

# Your Lambda Function URL (ensure this is the one you updated)
API_URL = "https://skivqtfkjd63bazhdlci2jx7rq0htusv.lambda-url.us-east-2.on.aws"

def test_root():
    """Test the root endpoint"""
    print(f"\n--- Testing Root URL ({API_URL}) ---")
    try:
        response = requests.get(API_URL)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

def test_get_clients():
    """Test GET /clients"""
    print(f"\n--- Testing GET {API_URL}/clients ---")
    try:
        # FastAPI might require a token if you have security enabled, 
        # but your code had 'Depends(get_token)' which accepts just a string for now?
        # Actually in app.py: get_token(auth: HTTPAuthorizationCredentials = Depends(security))
        # This requires an Authorization header: "Bearer <token>"
        
        headers = {
            "Authorization": "Bearer dummy_token"
        }
        
        response = requests.get(f"{API_URL}/clients", headers=headers)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            clients = data.get('clients', [])
            print(f"✅ SUCCESS: Retrieved {len(clients)} clients.")
            if len(clients) > 0:
                print(f"Sample client: {clients[0].get('legalName')}")
        else:
            print(f"❌ FAILED: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_root()
    test_get_clients()
