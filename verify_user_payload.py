import json
from lambda_function import create_client, ClientData
from pydantic import ValidationError

def clean_and_test_payload():
    raw_payload = """{
"id": "ORG-TEST-001",
"legalName": "Test Healthcare Services LLC",
"doingBusinessAs": "Test Health",
"companyName": "Test Healthcare Services",
"taxId": "12-3456789",
"industry": "Healthcare",
"address": "123 Main St, Suite 400, Chicago, IL 60601",
"billingAddress": "123 Main St, Suite 400, Chicago, IL 60601",
"addressStreet": "123 Main St",
"addressStreet2": "Suite 400",
"addressCity": "Chicago",
"addressState": "IL",
"addressZip": "60601",
"billingAddressStreet": "123 Main St",
"billingAddressStreet2": "Suite 400",
"billingAddressCity": "Chicago",
"billingAddressState": "IL",
"billingAddressZip": "60601",
"sameAsBusinessAddress": true,
"paymentTerms": "Net 30",
"timesheetCadence": "Weekly",
"invoiceMethod": "Email",
"vmsPortalType": "Fieldglass",
"vmsPortalUrl": "https://vendor.fieldglass.com",
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
],
"isExistingClient": false,
"requiresFullOnboarding": true,
"activeEngagements": 0,
"totalEngagementValue": 0,
"documentsComplete": false,
"contractSigned": false,
"canGenerateInvoices": false,
"onboardingStatus": "not-started",
"isActive": true,
"hasComplianceIssues": false,
"hasExpiringPOs": false,
"hasExpiringDocuments": false,
"mpaFile": {
"name": "Master_Professional_Agreement.pdf",
"content": "JVBERi0xLjUKJcfs...",
"type": "application/pdf"
},
"createdAt": "2026-01-06T10:15:30Z",
"updatedAt": "2026-01-06T10:15:30Z"
}"""
    
    # User had *true* / *false* in their text, need to clean that if pasting directly into code
    # But since I'm putting it in a python string, I can just replace valid JSON format
    # Actually the user request showed '*true*' which is not valid JSON. Swagger was failing on that.
    # The user's input likely came from a formatted doc where true/false were bolded or marked.
    
    # I will verify if this payload parses correctly as Pydantic model
    try:
        data = json.loads(raw_payload)
        print("✅ JSON is valid.")
        
        # Test creating the Pydantic model
        client = ClientData(**data)
        print("✅ Pydantic Model validated successfully.")
        
        # Try to run it against the local function if possible
        # We need to handle S3 mock if we run it
        print("Running locally...")
        result = create_client(client, token="test")
        print(f"✅ Success: {result}")
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON Parse Error: {e}")
    except ValidationError as e:
        print(f"❌ Pydantic Validation Error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    clean_and_test_payload()
