import lambda_function
from lambda_function import update_client, ClientData, Contact
import json

def test_update_direct():
    print("\n--- Testing 'update_client' directly ---")
    
    client_id = "11"
    
    # Construct ClientData object
    contact = Contact(
        contactType="Billing",
        name="Updated Admin",
        email="admin@update.com",
        phone="555-0123",
        isPrimary=True,
        canApproveTimesheets=True,
        canApproveInvoices=True
    )
    
    c_data = ClientData(
        id=client_id,
        legalName="Test Healthcare RE-UPDATED",
        doingBusinessAs="THC-New",
        companyName="Test Healthcare Inc V2",
        taxId="99-9999999",
        industry="Technology",
        address="999 Innovation Dr",
        billingAddress="999 Innovation Dr",
        paymentTerms="Net 60",
        timesheetCadence="Monthly",
        invoiceMethod="Portal",
        status="Inactive",
        contacts=[contact],
        isActive=True
    )
    
    try:
        # Call the function directly
        # token is mocked as a string
        response = update_client(client_id=client_id, client_data=c_data, token="dummy")
        print("\nResponse:")
        print(json.dumps(response, indent=2))
        print("\nSUCCESS: Client updated.")
        
    except Exception as e:
        print(f"\nFAILED: {e}")

if __name__ == "__main__":
    test_update_direct()
