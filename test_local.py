import lambda_function
import base64
import json
import os

# Create a dummy file for testing
dummy_content = b"This is a test document content from localhost."
encoded_content = base64.b64encode(dummy_content).decode('utf-8')

test_event = {
    "operation": "upload",
    "folder_path": "local_test_uploads/docs", 
    "file_name": "local_test_doc.txt",
    "file_content_base64": encoded_content,
    "metadata": {
        "uploaded_by": "local_tester",
        "doc_type": "test_text",
        "description": "Testing from localhost"
    }
}

# Mock context object that Lambda normally provides
class MockContext:
    def __init__(self):
        self.function_name = "test_function"
        self.memory_limit_in_mb = 128
        self.invoked_function_arn = "arn:aws:lambda:us-east-2:123456789012:function:test"
        self.aws_request_id = "test-request-id"

print("--- Starting Local Test ---")
print("Note: This test connects to real AWS S3 and RDS. Ensure you have 'aws configure' setup.")

try:
    response = lambda_function.lambda_handler(test_event, MockContext())
    print("\n--- Response ---")
    print(json.dumps(response, indent=2))
except Exception as e:
    print(f"\n[!] Test Failed: {e}")
    print("\nTroubleshooting Tips:")
    print("1. AWS Credentials: Run 'aws configure' in your terminal.")
    print("2. Database Table: Ensure the 'documents' table exists in your DB.")
    print("3. Network: Ensure your IP is allowed in the RDS Security Group.")
    print("4. Dependencies: Run 'pip install -r requirements.txt'")
