import lambda_function
import json

def test_delete_client():
    print("\n--- Testing 'delete_client' operation ---")
    
    # We'll delete the client we updated (ID 1)
    client_id = 1
    
    payload = {
        "operation": "delete_client",
        "clientId": client_id
    }
    
    # Mock Context
    class MockContext:
        def __init__(self):
            self.function_name = "test_function"
            self.memory_limit_in_mb = 128
            self.invoked_function_arn = "arn:aws:lambda:local:123456789012:function:test"
            self.aws_request_id = "test-delete-req"

    try:
        response = lambda_function.lambda_handler(payload, MockContext())
        print("\nDelete Response received:")
        print(json.dumps(response, indent=2))
        
        if response['statusCode'] == 200:
            print(f"\nSUCCESS: Client ID {client_id} and its contacts deleted successfully.")
        else:
            print(f"\nFAILED: Server returned error {response['statusCode']}")
            
    except Exception as e:
        print(f"\n[!] Local Test Crashed: {e}")

if __name__ == "__main__":
    test_delete_client()
