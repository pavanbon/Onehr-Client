import lambda_function
import json
import base64

def test_update_client():
    print("\n--- Testing 'update_client' operation ---")
    
    # We'll update the client we created earlier (ID 1)
    client_id = 11
    
    payload = {
        "operation": "update_client",
        "clientData": {
            "id": client_id,
            "legalName": "F Updated",
            "doingBusinessAs": "kldfj-updated",
            "companyName": "lkjdskl-inc",
            "taxId": "kjk-999",
            "industry": "Tech",
            "address": "123 Update St, New City",
            "billingAddress": "123 Update St, New City",
            "paymentTerms": "Net 45",
            "timesheetCadence": "Bi-Weekly",
            "invoiceMethod": "Portal",
            "vmsPortalType": "Beeline",
            "vmsPortalUrl": "updated-url.com",
            "status": "Active",
            "contacts": [
                {
                    "contactType": "Billing",
                    "name": "Updated Admin",
                    "email": "admin@update.com",
                    "phone": "555-0123",
                    "isPrimary": True,
                    "canApproveTimesheets": True,
                    "canApproveInvoices": True
                }
            ],
            "isActive": True
        }
    }
    
    # Mock Context
    class MockContext:
        def __init__(self):
            self.function_name = "test_function"
            self.memory_limit_in_mb = 128
            self.invoked_function_arn = "arn:aws:lambda:local:123456789012:function:test"
            self.aws_request_id = "test-update-req"

    try:
        response = lambda_function.lambda_handler(payload, MockContext())
        print("\nUpdate Response received:")
        print(json.dumps(response, indent=2))
        
        if response['statusCode'] == 200:
            print("\nSUCCESS: Client updated successfully.")
        else:
            print(f"\nFAILED: Server returned error {response['statusCode']}")
            
    except Exception as e:
        print(f"\n[!] Local Test Crashed: {e}")

if __name__ == "__main__":
    test_update_client()
