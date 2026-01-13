import json
import boto3
import pg8000.native
from lambda_function import get_clients

def test_get_clients():
    try:
        # Mocking the Depends(get_token) by just passing a string
        result = get_clients(token="dummy")
        print("Clients in DB:")
        for c in result['clients']:
            if str(c['id']) == "11":
                print(f"\n--- CLIENT 11 DETAILS ---")
                print(f"Name: {c.get('legalName')}")
                print(f"Status: {c.get('status')}")
                print(f"Industry: {c.get('industry')}")
                print(f"Payment Terms: {c.get('paymentTerms')}")
                print(f"Address: {c.get('address')}")
                print("-------------------------")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_get_clients()
