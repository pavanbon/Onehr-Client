import json
import boto3
import pg8000.native
from lambda_function import ClientData, create_client
from pydantic import ValidationError

# Mock token
class MockAuth:
    def __init__(self, credentials):
        self.credentials = credentials

def test_insertion():
    payload = {
        "id": "ORG-TEST-002",
        "legalName": "Test Healthcare Services LLC",
        "doingBusinessAs": "Test Health",
        "companyName": "Test Healthcare Services",
        "taxId": "12-3456789",
        "industry": "Healthcare",
        "address": "123 Main St, Suite 400, Chicago, IL 60601",
        "status": "New",
        "contacts": [
            {
                "contactId": "CONT-001",
                "name": "John Doe",
                "email": "john.doe@testhealth.com",
                "phone": "3125557890",
                "role": "Accounts Payable"
            }
        ],
        "documents": [
            {
                "documentId": "DOC-001",
                "documentType": "W9",
                "status": "Pending"
            }
        ]
    }
    
    try:
        client_data = ClientData(**payload)
        print("Payload valid. Attempting to insert...")
        # We call the function directly. 
        # Note: Depends(get_token) won't run normally here, but we can pass a dummy token
        result = create_client(client_data, token="dummy-token")
        print("Success!")
        print(result)
    except Exception as e:
        print(f"Error during insertion: {e}")

if __name__ == "__main__":
    test_insertion()
