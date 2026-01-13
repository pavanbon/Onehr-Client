from lambda_function import ClientData
import json
from pydantic import ValidationError

payload = {
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
"sameAsBusinessAddress": True,
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
"isExistingClient": False,
"requiresFullOnboarding": True,
"activeEngagements": 0,
"totalEngagementValue": 0,
"documentsComplete": False,
"contractSigned": False,
"canGenerateInvoices": False,
"onboardingStatus": "not-started",
"isActive": True,
"hasComplianceIssues": False,
"hasExpiringPOs": False,
"hasExpiringDocuments": False,
"mpaFile": {
"name": "Master_Professional_Agreement.pdf",
"content": "JVBERi0xLjUKJcfs...",
"type": "application/pdf"
},
"createdAt": "2026-01-06T10:15:30Z",
"updatedAt": "2026-01-06T10:15:30Z"
}

try:
    print("Validating payload...")
    client_data = ClientData(**payload)
    print("Payload is valid!")
    print("\n--- Parsed Data (what the function receives) ---")
    print(client_data.model_dump(exclude_unset=True))
    
    # specific checks
    if not client_data.contacts:
        print("\nWARNING: No contacts parsed.")
    else:
        print(f"\nParsed {len(client_data.contacts)} contacts.")
        if client_data.contacts[0].id == "CONT-001":
             print("SUCCESS: Contact 'contactId' mapped to 'id' successfully.")
        else:
             print(f"WARNING: Contact ID is '{client_data.contacts[0].id}' (Expected 'CONT-001').")

    if not client_data.documents:
        print("WARNING: No documents parsed.")
    else:
        if client_data.documents[0].id == "DOC-001":
            print("SUCCESS: Document 'documentId' mapped to 'id' successfully.")
        else:
            print(f"WARNING: Document ID is '{client_data.documents[0].id}' (Expected 'DOC-001').")

except ValidationError as e:
    print("Validation Error:")
    print(e)
