import json
import boto3
import base64
import os
from threading import Lock
from typing import List, Optional, Any
from fastapi import FastAPI, HTTPException, Body, Depends, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from mangum import Mangum
from pydantic import BaseModel, Field
import pg8000.native

# Initialize FastAPI
app = FastAPI(title="OneHR 2.0 API", description="Client & Document Management Service")

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

def get_token(auth: HTTPAuthorizationCredentials = Depends(security)):
    return auth.credentials

# Initialize AWS clients
s3_client = boto3.client('s3')
secrets_client = boto3.client('secretsmanager', region_name='us-east-2')
SECRET_NAME = 'rds!db-9888f9d1-be9e-4215-ba07-02fdf234cac4'
BUCKET_NAME = os.environ.get('S3_BUCKET_NAME', 'onehr-bucket')

# --- Pydantic Models ---
class Contact(BaseModel):
    id: Optional[str] = Field(None, alias="contactId")
    contactType: Optional[str] = "General"
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    isPrimary: bool = False
    canApproveTimesheets: bool = False
    canApproveInvoices: bool = False

class Document(BaseModel):
    id: Optional[str] = Field(None, alias="documentId")
    fileName: Optional[str] = None
    filePath: Optional[str] = None
    fileSize: Optional[int] = 0
    documentType: Optional[str] = "General"
    uploadedAt: Optional[str] = None
    uploadedBy: Optional[str] = "Admin"
    status: Optional[str] = "approved"

class FileUpload(BaseModel):
    name: Optional[str] = None
    content: Optional[str] = None
    type: Optional[str] = None

class ClientData(BaseModel):
    id: Optional[str] = None
    legalName: Optional[str] = None
    doingBusinessAs: Optional[str] = None
    companyName: Optional[str] = None
    taxId: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    industry: Optional[str] = None
    address: Optional[str] = None
    billingAddress: Optional[str] = None
    addressStreet: Optional[str] = None
    addressStreet2: Optional[str] = None
    addressCity: Optional[str] = None
    addressState: Optional[str] = None
    addressZip: Optional[str] = None
    billingAddressStreet: Optional[str] = None
    billingAddressStreet2: Optional[str] = None
    billingAddressCity: Optional[str] = None
    billingAddressState: Optional[str] = None
    billingAddressZip: Optional[str] = None
    sameAsBusinessAddress: bool = True
    paymentTerms: Optional[str] = "Net 30"
    timesheetCadence: Optional[str] = "Weekly"
    invoiceMethod: Optional[str] = "Email"
    vmsPortalType: Optional[str] = None
    vmsPortalUrl: Optional[str] = None
    status: str = "New"
    contacts: List[Contact] = []
    documents: List[Document] = []
    isExistingClient: bool = False
    requiresFullOnboarding: bool = True
    activeEngagements: int = 0
    totalEngagementValue: float = 0.0
    documentsComplete: bool = False
    contractSigned: bool = False
    canGenerateInvoices: bool = False
    onboardingStatus: str = "not-started"
    isActive: bool = True
    hasComplianceIssues: bool = False
    hasExpiringPOs: bool = False
    hasExpiringDocuments: bool = False
    mpaFile: Optional[FileUpload] = None
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None
    engagements: List[Any] = []

class Contract(BaseModel):
    id: Optional[str] = None
    clientId: Optional[str] = Field(None, alias="clientId")
    title: str
    contractType: Optional[str] = Field("Time & Materials", alias="type")
    startDate: str = Field(..., alias="startDate")
    endDate: Optional[str] = Field(None, alias="endDate")
    status: Optional[str] = "Active"
    documentId: Optional[str] = Field(None, alias="documentId")

class ContractAddendum(BaseModel):
    id: Optional[str] = None
    contractId: str = Field(..., alias="contractId")
    title: str
    description: Optional[str] = None
    documentId: Optional[str] = Field(None, alias="documentId")
    signedDate: Optional[str] = Field(None, alias="signedDate")

class PurchaseOrder(BaseModel):
    id: Optional[str] = None
    clientId: Optional[str] = Field(None, alias="clientId")
    contractId: Optional[str] = Field(None, alias="contractId")
    poNumber: str = Field(..., alias="poNumber")
    totalAmount: float = Field(..., alias="amount")
    spentAmount: float = 0.0
    remainingAmount: Optional[float] = None
    startDate: str = Field(..., alias="startDate")
    endDate: Optional[str] = Field(None, alias="endDate")
    status: Optional[str] = "Active"
    poType: Optional[str] = "Standard"
    documentId: Optional[str] = Field(None, alias="documentId")

class Requirement(BaseModel):
    id: Optional[str] = None
    clientId: Optional[str] = Field(None, alias="clientId")
    title: str
    description: Optional[str] = None
    category: Optional[str] = "Compliance"
    isMandatory: bool = True

class RequirementInstance(BaseModel):
    id: Optional[str] = None
    requirementId: str = Field(..., alias="requirementId")
    employeeId: str = Field(..., alias="employeeId")
    status: str = "Pending"
    documentId: Optional[str] = None
    expiryDate: Optional[str] = None

class ClientPortalUser(BaseModel):
    id: Optional[str] = None
    clientId: str = Field(..., alias="clientId")
    email: str
    role: str = "Admin"
    isActive: bool = True

class Project(BaseModel):
    id: Optional[str] = None
    clientId: str = Field(..., alias="clientId")
    projectName: str = Field(..., alias="projectName")
    description: Optional[str] = None
    startDate: str = Field(..., alias="startDate")
    endDate: Optional[str] = Field(None, alias="endDate")
    status: str = "Active"
    budget: Optional[float] = None

class Assignment(BaseModel):
    id: Optional[str] = None
    clientId: str = Field(..., alias="clientId")
    employeeId: str = Field(..., alias="employeeId")
    projectId: Optional[str] = Field(None, alias="projectId")
    role: Optional[str] = "Consultant"
    startDate: Optional[str] = None
    status: str = "Active"

@app.get("/", tags=["Health"])
def read_root():
    db_status = "Unknown"
    try:
        conn = get_db_connection()
        conn.run("SELECT 1")
        conn.close()
        db_status = "Connected"
    except Exception as e:
        db_status = f"Error: {str(e)}"

    return {
        "status": "healthy",
        "database": db_status,
        "message": "OneHR 2.0 API is running!",
        "version": "2.0.1",
        "docs": "/docs"
    }

def get_db_connection():
    try:
        secret = json.loads(secrets_client.get_secret_value(SecretId=SECRET_NAME)['SecretString'])
        conn = pg8000.native.Connection(
            host="hr.cx00uaqeg0tv.us-east-2.rds.amazonaws.com",
            database=secret.get('dbname', 'onehr'),
            user=secret.get('username'),
            password=secret.get('password'),
            port=int(secret.get('port', 5432))
        )
        return conn
    except Exception as e:
        print(f"DB Connect Error: {e}")
        raise HTTPException(status_code=500, detail="Database connection failed")

def upload_to_s3(client_id, file_name, file_content, content_type, doc_type):
    try:
        # Decode base64 if needed
        if isinstance(file_content, str) and ',' in file_content:
            file_content = file_content.split(',')[1]
        
        if isinstance(file_content, str):
            file_bytes = base64.b64decode(file_content)
        else:
            file_bytes = file_content # Assume bytes

        s3_key = f"clients/{client_id}/{doc_type}/{file_name}"
        s3_client.put_object(Bucket=BUCKET_NAME, Key=s3_key, Body=file_bytes, ContentType=content_type)
        
        # Record in documents table
        conn = get_db_connection()
        query = "INSERT INTO documents (file_path, bucket_name, doc_type, client_id, uploaded_at) VALUES (:p, :b, :dt, :cid, NOW()) RETURNING id"
        res = conn.run(query, p=s3_key, b=BUCKET_NAME, dt=doc_type, cid=client_id)
        doc_id = str(res[0][0])
        conn.close()
        return doc_id, s3_key
    except Exception as e:
        print(f"S3 Upload Error: {e}")
        return None, None

# --- Routes ---

@app.get("/clients")
def get_clients(token: str = Depends(get_token)):
    conn = None
    try:
        conn = get_db_connection()
        # 1. Fetch Clients
        client_rows = conn.run("SELECT * FROM clients ORDER BY created_at DESC")
        cols = [d['name'] for d in conn.columns]
        
        clients = []
        for row in client_rows:
            c = dict(zip(cols, row))
            client_id = c['id']
            
            # 2. Fetch Contacts (using correct database column names)
            contact_rows = conn.run("SELECT * FROM client_contacts WHERE client_id = :cid", cid=client_id)
            contact_cols = [d['name'] for d in conn.columns]
            contacts = []
            for cr in contact_rows:
                cd = dict(zip(contact_cols, cr))
                contacts.append({
                    "id": str(cd.get('id')),
                    "clientId": str(cd.get('client_id')),
                    "contactType": cd.get('contact_type'),
                    "name": cd.get('name'), 
                    "email": cd.get('email'), 
                    "phone": cd.get('phone'), 
                    "isPrimary": cd.get('is_primary'),
                    "canApproveTimesheets": cd.get('can_approve_timesheets'),
                    "canApproveInvoices": cd.get('can_approve_invoices')
                })
            
            # 3. Fetch Documents (using correct table name documents)
            doc_rows = conn.run("SELECT * FROM documents WHERE client_id = :cid", cid=client_id)
            doc_cols = [d['name'] for d in conn.columns]
            docs = []
            for dr in doc_rows:
                dd = dict(zip(doc_cols, dr))
                fpath = dd.get('file_path') or ''
                filename = fpath.split('/')[-1]
                docs.append({
                    "id": str(dd.get('id')),
                    "clientId": str(dd.get('client_id')),
                    "fileName": filename,
                    "filePath": fpath,
                    "documentType": dd.get('doc_type'),
                    "uploadedAt": str(dd.get('uploaded_at')),
                    "fileUploaded": True,
                    "status": "approved"
                })

            clients.append({
                "id": str(c['id']),
                "legalName": c.get('legal_name'),
                "companyName": c.get('company_name'),
                "taxId": c.get('tax_id'),
                "industry": c.get('industry'),
                "status": c.get('status'),
                "address": c.get('address'),
                "doingBusinessAs": c.get('doing_business_as'),
                "onboardingStatus": c.get('onboarding_status'),
                "paymentTerms": c.get('payment_terms'),
                "timesheetCadence": c.get('timesheet_cadence'),
                "invoiceMethod": c.get('invoice_method'),
                "vmsPortalUrl": c.get('vms_portal_url'),
                "vmsPortalType": c.get('vms_portal_type'),
                "isActive": c.get('is_active'),
                "contacts": contacts,
                "documents": docs,
                "employees": [],
                "engagements": []
            })
        return {"clients": clients}
    finally:
        if conn: conn.close()

@app.post("/clients")
def create_client(client_data: ClientData, token: str = Depends(get_token)):
    conn = None
    try:
        conn = get_db_connection()
        
        # Detect columns dynamically
        cols = [r[0] for r in conn.run("SELECT column_name FROM information_schema.columns WHERE table_name='clients'")]
        
        # Mapping from Pydantic fields to DB columns (handles multiple names)
        mapping = {
            "legal_name": client_data.legalName,
            "company_name": client_data.companyName,
            "tax_id": client_data.taxId,
            "industry": client_data.industry,
            "status": client_data.status,
            "payment_terms": client_data.paymentTerms,
            "timesheet_cadence": client_data.timesheetCadence,
            "invoice_method": client_data.invoiceMethod,
            "vms_portal_type": client_data.vmsPortalType,
            "vms_portal_url": client_data.vmsPortalUrl,
            "onboarding_status": client_data.onboardingStatus,
            "is_active": client_data.isActive,
            "is_existing_client": client_data.isExistingClient,
            "requires_full_onboarding": client_data.requiresFullOnboarding,
            "same_as_business_address": client_data.sameAsBusinessAddress,
            "active_engagements": client_data.activeEngagements,
            "total_engagement_value": client_data.totalEngagementValue,
            "documents_complete": client_data.documentsComplete,
            "contract_signed": client_data.contractSigned,
            "can_generate_invoices": client_data.canGenerateInvoices,
            "has_compliance_issues": client_data.hasComplianceIssues,
            "has_expiring_pos": client_data.hasExpiringPOs,
            "has_expiring_documents": client_data.hasExpiringDocuments,
        }
        
        # Handle Schema Differences
        if "doing_business_as" in cols: mapping["doing_business_as"] = client_data.doingBusinessAs
        elif "dba_name" in cols: mapping["dba_name"] = client_data.doingBusinessAs
        
        if "email" in cols: mapping["email"] = client_data.email or (client_data.contacts[0].email if client_data.contacts else None)
        if "phone" in cols: mapping["phone"] = client_data.phone or (client_data.contacts[0].phone if client_data.contacts else None)
        
        # Mandatory field for onehr database
        if "created_by" in cols:
            mapping["created_by"] = "c4557798-8db1-4397-9120-a50a2652411d" # System User ID
        
        if "address" in cols: mapping["address"] = client_data.address
        if "business_address" in cols: mapping["business_address"] = client_data.address
        if "billing_address" in cols: mapping["billing_address"] = client_data.billingAddress
        
        if "address_street" in cols: mapping["address_street"] = client_data.addressStreet
        if "address_street2" in cols: mapping["address_street2"] = client_data.addressStreet2
        if "address_city" in cols: mapping["address_city"] = client_data.addressCity
        elif "city" in cols: mapping["city"] = client_data.addressCity
        
        if "address_state" in cols: mapping["address_state"] = client_data.addressState
        elif "state" in cols: mapping["state"] = client_data.addressState
        
        if "address_zip" in cols: mapping["address_zip"] = client_data.addressZip
        elif "zip_code" in cols: mapping["zip_code"] = client_data.addressZip
        elif "zip" in cols: mapping["zip"] = client_data.addressZip
        
        if "billing_address_street" in cols: mapping["billing_address_street"] = client_data.billingAddressStreet
        if "billing_address_street2" in cols: mapping["billing_address_street2"] = client_data.billingAddressStreet2
        if "billing_address_city" in cols: mapping["billing_address_city"] = client_data.billingAddressCity
        if "billing_address_state" in cols: mapping["billing_address_state"] = client_data.billingAddressState
        if "billing_address_zip" in cols: mapping["billing_address_zip"] = client_data.billingAddressZip

        # Filter mapping by existing columns
        final_data = {k: v for k, v in mapping.items() if k in cols}
        
        # Build Query
        fields = ", ".join(final_data.keys())
        placeholders = ", ".join([f":{k}" for k in final_data.keys()])
        query = f"INSERT INTO clients ({fields}, created_at, updated_at) VALUES ({placeholders}, NOW(), NOW()) RETURNING id"
        
        res = conn.run(query, **final_data)
        
        new_id = res[0][0]
        
        # Insert Contacts
        for contact in client_data.contacts:
            conn.run("""
                INSERT INTO client_contacts (client_id, contact_type, name, email, phone, is_primary, can_approve_timesheets, can_approve_invoices)
                VALUES (:cid, :type, :name, :email, :phone, :primary, :cats, :cai)
            """, cid=new_id, type=contact.contactType, name=contact.name, email=contact.email, 
                 phone=contact.phone, primary=contact.isPrimary, cats=contact.canApproveTimesheets, cai=contact.canApproveInvoices)

        # Handle File Upload
        if client_data.mpaFile and client_data.mpaFile.content:
            upload_to_s3(new_id, client_data.mpaFile.name, client_data.mpaFile.content, client_data.mpaFile.type, "MSA")

        # Insert Documents (Status/Checklist)
        for doc in client_data.documents:
            # Check if this is an uploaded file or just status
            # We assume these are status trackers. 
            # If doc.id (documentId) is present, store it as external_id (if column exists)
            # Use empty string for file_path if not provided/null 
            
            # Check tables columns dynamically or assume 'status' exists now.
            # Using try-except to handle schema variations gracefully
            try:
                conn.run("""
                    INSERT INTO documents (client_id, doc_type, status, file_path, uploaded_at)
                    VALUES (:cid, :dtype, :status, '', NOW())
                """, cid=new_id, dtype=doc.documentType, status=doc.status)
            except Exception as doc_err:
                 print(f"Warning: Could not insert document {doc.documentType}: {doc_err}")

        return {"message": "Client created successfully", "id": str(new_id)}
    except Exception as e:
        print(f"Error creating client: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn: conn.close()

@app.put("/clients/{client_id}")
def update_client(client_id: str, client_data: ClientData, token: str = Depends(get_token)):
    conn = None
    try:
        conn = get_db_connection()
        
        # Detect columns dynamically
        cols = [r[0] for r in conn.run("SELECT column_name FROM information_schema.columns WHERE table_name='clients'")]
        
        # Mapping from Pydantic fields to DB columns
        mapping = {
            "legal_name": client_data.legalName,
            "company_name": client_data.companyName,
            "tax_id": client_data.taxId,
            "industry": client_data.industry,
            "status": client_data.status,
            "payment_terms": client_data.paymentTerms,
            "timesheet_cadence": client_data.timesheetCadence,
            "invoice_method": client_data.invoiceMethod,
            "vms_portal_type": client_data.vmsPortalType,
            "vms_portal_url": client_data.vmsPortalUrl,
            "onboarding_status": client_data.onboardingStatus,
            "is_active": client_data.isActive,
            "is_existing_client": client_data.isExistingClient,
            "requires_full_onboarding": client_data.requiresFullOnboarding,
            "same_as_business_address": client_data.sameAsBusinessAddress,
            "active_engagements": client_data.activeEngagements,
            "total_engagement_value": client_data.totalEngagementValue,
            "documents_complete": client_data.documentsComplete,
            "contract_signed": client_data.contractSigned,
            "can_generate_invoices": client_data.canGenerateInvoices,
            "has_compliance_issues": client_data.hasComplianceIssues,
            "has_expiring_pos": client_data.hasExpiringPOs,
            "has_expiring_documents": client_data.hasExpiringDocuments,
        }
        
        if "doing_business_as" in cols: mapping["doing_business_as"] = client_data.doingBusinessAs
        elif "dba_name" in cols: mapping["dba_name"] = client_data.doingBusinessAs
        
        if "email" in cols: mapping["email"] = client_data.email or (client_data.contacts[0].email if client_data.contacts else None)
        if "phone" in cols: mapping["phone"] = client_data.phone or (client_data.contacts[0].phone if client_data.contacts else None)
        
        if "address" in cols: mapping["address"] = client_data.address
        if "business_address" in cols: mapping["business_address"] = client_data.address
        if "billing_address" in cols: mapping["billing_address"] = client_data.billingAddress
        
        if "address_street" in cols: mapping["address_street"] = client_data.addressStreet
        if "address_street2" in cols: mapping["address_street2"] = client_data.addressStreet2
        if "address_city" in cols: mapping["address_city"] = client_data.addressCity
        elif "city" in cols: mapping["city"] = client_data.addressCity
        
        if "address_state" in cols: mapping["address_state"] = client_data.addressState
        elif "state" in cols: mapping["state"] = client_data.addressState
        
        if "address_zip" in cols: mapping["address_zip"] = client_data.addressZip
        elif "zip_code" in cols: mapping["zip_code"] = client_data.addressZip
        
        if "billing_address_street" in cols: mapping["billing_address_street"] = client_data.billingAddressStreet
        if "billing_address_street2" in cols: mapping["billing_address_street2"] = client_data.billingAddressStreet2
        if "billing_address_city" in cols: mapping["billing_address_city"] = client_data.billingAddressCity
        if "billing_address_state" in cols: mapping["billing_address_state"] = client_data.billingAddressState
        if "billing_address_zip" in cols: mapping["billing_address_zip"] = client_data.billingAddressZip

        final_data = {k: v for k, v in mapping.items() if k in cols}
        
        # Build Update Query
        updates = ", ".join([f"{k} = :{k}" for k in final_data.keys()])
        query = f"UPDATE clients SET {updates}, updated_at = NOW() WHERE id = :target_id"
        
        final_data["target_id"] = client_id
        conn.run(query, **final_data)

        # Update Contacts (Delete and re-insert)
        conn.run("DELETE FROM client_contacts WHERE client_id = :id", id=client_id)
        for contact in client_data.contacts:
            conn.run("""
                INSERT INTO client_contacts (client_id, contact_type, name, email, phone, is_primary, can_approve_timesheets, can_approve_invoices)
                VALUES (:cid, :type, :name, :email, :phone, :primary, :cats, :cai)
            """, cid=client_id, type=contact.contactType, name=contact.name, email=contact.email, 
                 phone=contact.phone, primary=contact.isPrimary, cats=contact.canApproveTimesheets, cai=contact.canApproveInvoices)

        # Handle File Upload
        if client_data.mpaFile and client_data.mpaFile.content:
            upload_to_s3(client_id, client_data.mpaFile.name, client_data.mpaFile.content, client_data.mpaFile.type, "MSA")

        return {"message": "Client updated successfully"}
    except Exception as e:
        print(f"Error updating client: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn: conn.close()


@app.delete("/clients/{client_id}")
def delete_client(client_id: str, token: str = Depends(get_token)):
    conn = None
    try:
        conn = get_db_connection()
        conn.run("DELETE FROM client_contacts WHERE client_id = :id", id=client_id)
        conn.run("DELETE FROM clients WHERE id = :id", id=client_id)
        return {"message": "Deleted"}
    finally:
        if conn: conn.close()

# Mangum Handler
# --- Advanced & Blueprint Endpoints ---

@app.get("/clients/advanced", tags=["Advanced"])
def get_clients_advanced(token: str = Depends(get_token)):
    return get_clients(token)

@app.post("/clients/advanced", tags=["Advanced"])
def create_client_advanced(client_data: ClientData = Body(...), token: str = Depends(get_token)):
    return create_client(client_data, token)

@app.get("/clients/advanced/{client_id}", tags=["Advanced"])
def get_client_advanced(client_id: str, token: str = Depends(get_token)):
    conn = None
    try:
        conn = get_db_connection()
        res = conn.run("SELECT * FROM clients WHERE id = :id", id=client_id)
        if not res: raise HTTPException(status_code=404, detail="Client not found")
        cols = [d['name'] for d in conn.columns]
        c = dict(zip(cols, res[0]))
        
        # Contacts
        rows = conn.run("SELECT * FROM client_contacts WHERE client_id = :id", id=client_id)
        ccols = [d['name'] for d in conn.columns]
        contacts = []
        for r in rows:
            cd = dict(zip(ccols, r))
            contacts.append({
                "id": str(cd.get('id')),
                "name": cd.get('name'),
                "email": cd.get('email'),
                "phone": cd.get('phone'),
                "contactType": cd.get('contact_type'),
                "isPrimary": cd.get('is_primary'),
                "canApproveTimesheets": cd.get('can_approve_timesheets'),
                "canApproveInvoices": cd.get('can_approve_invoices')
            })

        # Documents
        rows = conn.run("SELECT * FROM documents WHERE client_id = :id", id=client_id)
        dcols = [d['name'] for d in conn.columns]
        documents = []
        for r in rows:
            dd = dict(zip(dcols, r))
            documents.append({
                "id": str(dd.get('id')),
                "fileName": (dd.get('file_path') or '').split('/')[-1],
                "documentType": dd.get('doc_type'),
                "uploadedAt": str(dd.get('uploaded_at')),
                "status": "approved"
            })

        # Engagements (Contracts)
        rows = conn.run("SELECT * FROM contracts WHERE client_id = :id", id=client_id)
        ecols = [d['name'] for d in conn.columns]
        engagements = []
        for r in rows:
            ed = dict(zip(ecols, r))
            # POs for this contract
            porows = conn.run("SELECT * FROM purchase_orders WHERE contract_id = :cid", cid=ed['id'])
            pocols = [d['name'] for d in conn.columns]
            pos = []
            for pr in porows:
                pd = dict(zip(pocols, pr))
                pos.append({
                    "id": str(pd['id']),
                    "poNumber": pd['po_number'],
                    "amount": float(pd['total_amount']),
                    "remainingAmount": float(pd['remaining_amount']),
                    "startDate": str(pd['start_date']),
                    "endDate": str(pd['end_date']),
                    "status": pd['status']
                })

            engagements.append({
                "id": str(ed['id']),
                "title": ed['title'],
                "type": ed['contract_type'],
                "startDate": str(ed['start_date']),
                "endDate": str(ed['end_date']),
                "status": ed['status'],
                "documentId": str(ed['document_id']) if ed.get('document_id') else None,
                "purchaseOrders": pos
            })

        return {
            "client": {
                **{k: c.get(k) for k in cols},
                "id": str(c['id']),
                "contacts": contacts,
                "documents": documents,
                "engagements": engagements
            }
        }
    finally:
        if conn: conn.close()

@app.put("/clients/advanced/{client_id}", tags=["Advanced"])
def update_client_advanced(client_id: str, payload: dict = Body(...), token: str = Depends(get_token)):
    conn = None
    try:
        conn = get_db_connection()
        # Handle Engagements (Contracts) Sync
        if "engagements" in payload:
            for eng in payload["engagements"]:
                # The frontend might send 'id' or not. If it's a new one, we insert.
                # Use COALESCE or INSERT ... ON CONFLICT
                eng_id = eng.get('id')
                if not eng_id:
                     # This shouldn't normally happen with your frontend code as it uses crypto.randomUUID()
                     # but we handle it just in case.
                     pass 
                
                conn.run("""
                    INSERT INTO contracts (id, client_id, title, contract_type, start_date, end_date, status)
                    VALUES (:id, :cid, :title, :type, :start, :end, :status)
                    ON CONFLICT (id) DO UPDATE SET 
                        title = EXCLUDED.title, contract_type = EXCLUDED.contract_type,
                        start_date = EXCLUDED.start_date, end_date = EXCLUDED.end_date, status = EXCLUDED.status
                """, id=eng.get('id'), cid=client_id, title=eng.get('title'), type=eng.get('type'),
                   start=eng.get('startDate'), end=eng.get('endDate'), status=eng.get('status'))
            
            # If payload ONLY had engagements, return now
            if len(payload) == 1:
                return {"message": "Engagements updated"}
        
        # Otherwise handle full client update if fields are present
        if "legalName" in payload or "companyName" in payload:
            client_data = ClientData(**payload)
            return update_client(client_id, client_data, token)
            
        return {"message": "Update processed"}
    finally:
        if conn: conn.close()

@app.get("/clients/{client_id}/contracts", tags=["Contracts"])
def get_client_contracts(client_id: str, token: str = Depends(get_token)):
    conn = None
    try:
        conn = get_db_connection()
        rows = conn.run("SELECT * FROM contracts WHERE client_id = :id", id=client_id)
        cols = [d['name'] for d in conn.columns]
        return {"contracts": [dict(zip(cols, r)) for r in rows]}
    finally:
        if conn: conn.close()

@app.post("/contracts", tags=["Contracts"])
def create_contract_general(contract: Contract, token: str = Depends(get_token)):
    conn = None
    try:
        conn = get_db_connection()
        query = "INSERT INTO contracts (client_id, title, contract_type, start_date, end_date, status, document_id) VALUES (:cid, :t, :type, :s, :e, :stat, :did) RETURNING id"
        res = conn.run(query, cid=contract.clientId, t=contract.title, type=contract.contractType, s=contract.startDate, e=contract.endDate, stat=contract.status, did=contract.documentId)
        return {"id": str(res[0][0])}
    finally:
        if conn: conn.close()

@app.put("/contracts/{contract_id}", tags=["Contracts"])
def update_contract(contract_id: str, contract: Contract, token: str = Depends(get_token)):
    conn = None
    try:
        conn = get_db_connection()
        query = "UPDATE contracts SET title=:t, contract_type=:type, start_date=:s, end_date=:e, status=:stat, document_id=:did, updated_at=NOW() WHERE id=:id"
        conn.run(query, id=contract_id, t=contract.title, type=contract.contractType, s=contract.startDate, e=contract.endDate, stat=contract.status, did=contract.documentId)
        return {"message": "Updated"}
    finally:
        if conn: conn.close()

@app.get("/contracts/{contract_id}", tags=["Contracts"])
def get_contract(contract_id: str, token: str = Depends(get_token)):
    conn = None
    try:
        conn = get_db_connection()
        res = conn.run("SELECT * FROM contracts WHERE id = :id", id=contract_id)
        if not res: raise HTTPException(404, "Not Found")
        cols = [d['name'] for d in conn.columns]
        return dict(zip(cols, res[0]))
    finally:
        if conn: conn.close()

@app.get("/contracts/{contract_id}/addendums", tags=["Contracts"])
def get_addendums(contract_id: str, token: str = Depends(get_token)):
    conn = None
    try:
        conn = get_db_connection()
        rows = conn.run("SELECT * FROM contract_addendums WHERE contract_id = :id", id=contract_id)
        cols = [d['name'] for d in conn.columns]
        return {"addendums": [dict(zip(cols, r)) for r in rows]}
    finally:
        if conn: conn.close()

@app.get("/clients/{client_id}/purchase-orders", tags=["POs"])
def get_client_pos(client_id: str, token: str = Depends(get_token)):
    conn = None
    try:
        conn = get_db_connection()
        rows = conn.run("SELECT * FROM purchase_orders WHERE client_id = :id", id=client_id)
        cols = [d['name'] for d in conn.columns]
        return {"purchase_orders": [dict(zip(cols, r)) for r in rows]}
    finally:
        if conn: conn.close()

@app.get("/purchase-orders/{po_id}", tags=["POs"])
def get_po(po_id: str, token: str = Depends(get_token)):
    conn = None
    try:
        conn = get_db_connection()
        res = conn.run("SELECT * FROM purchase_orders WHERE id = :id", id=po_id)
        if not res: raise HTTPException(404, "Not Found")
        cols = [d['name'] for d in conn.columns]
        return dict(zip(cols, res[0]))
    finally:
        if conn: conn.close()

@app.put("/purchase-orders/{po_id}", tags=["POs"])
def update_po(po_id: str, po: PurchaseOrder, token: str = Depends(get_token)):
    conn = None
    try:
        conn = get_db_connection()
        query = """
            UPDATE purchase_orders SET po_number=:num, total_amount=:amt, remaining_amount=:rem, 
            start_date=:s, end_date=:e, status=:stat, po_type=:type, updated_at=NOW() WHERE id=:id
        """
        conn.run(query, id=po_id, num=po.poNumber, amt=po.totalAmount, rem=po.remainingAmount or po.totalAmount,
                 s=po.startDate, e=po.endDate, stat=po.status, type=po.poType)
        return {"message": "Updated"}
    finally:
        if conn: conn.close()

@app.get("/purchase-orders/{po_id}/terms", tags=["POs"])
def get_po_terms(po_id: str, token: str = Depends(get_token)):
    # Assuming terms are just fields in PO for now
    return get_po(po_id, token)

@app.get("/clients/{client_id}/requirements", tags=["Requirements"])
def get_requirements(client_id: str, token: str = Depends(get_token)):
    conn = None
    try:
        conn = get_db_connection()
        rows = conn.run("SELECT * FROM client_requirements WHERE client_id = :id", id=client_id)
        cols = [d['name'] for d in conn.columns]
        return {"requirements": [dict(zip(cols, r)) for r in rows]}
    finally:
        if conn: conn.close()

@app.get("/requirements/instances", tags=["Requirements"])
def get_req_instances(employee_id: Optional[str] = None, token: str = Depends(get_token)):
    conn = None
    try:
        conn = get_db_connection()
        if employee_id:
            rows = conn.run("SELECT * FROM requirement_instances WHERE employee_id = :id", id=employee_id)
        else:
            rows = conn.run("SELECT * FROM requirement_instances")
        cols = [d['name'] for d in conn.columns]
        return {"instances": [dict(zip(cols, r)) for r in rows]}
    finally:
        if conn: conn.close()

@app.get("/client-portal/users", tags=["Portal"])
def get_portal_users(client_id: Optional[str] = None, token: str = Depends(get_token)):
    conn = None
    try:
        conn = get_db_connection()
        if client_id:
            rows = conn.run("SELECT * FROM client_portal_users WHERE client_id = :id", id=client_id)
        else:
            rows = conn.run("SELECT * FROM client_portal_users")
        cols = [d['name'] for d in conn.columns]
        return {"users": [dict(zip(cols, r)) for r in rows]}
    finally:
        if conn: conn.close()

@app.post("/client-portal/users", tags=["Portal"])
def create_portal_user(user: ClientPortalUser, token: str = Depends(get_token)):
    conn = None
    try:
        conn = get_db_connection()
        query = "INSERT INTO client_portal_users (client_id, email, role, is_active) VALUES (:cid, :email, :role, :act) RETURNING id"
        res = conn.run(query, cid=user.clientId, email=user.email, role=user.role, act=user.isActive)
        return {"id": str(res[0][0])}
    finally:
        if conn: conn.close()

@app.post("/clients/{client_id}/requirements", tags=["Requirements"])
def create_requirement(client_id: str, req: Requirement, token: str = Depends(get_token)):
    conn = None
    try:
        conn = get_db_connection()
        query = "INSERT INTO client_requirements (client_id, title, description, category, is_mandatory) VALUES (:cid, :t, :d, :c, :m) RETURNING id"
        res = conn.run(query, cid=client_id, t=req.title, d=req.description, c=req.category, m=req.isMandatory)
        return {"id": str(res[0][0])}
    finally:
        if conn: conn.close()

@app.post("/requirements/instances", tags=["Requirements"])
def create_req_instance(inst: RequirementInstance, token: str = Depends(get_token)):
    conn = None
    try:
        conn = get_db_connection()
        query = "INSERT INTO requirement_instances (requirement_id, employee_id, status, document_id, expiry_date) VALUES (:rid, :eid, :s, :did, :exp) RETURNING id"
        res = conn.run(query, rid=inst.requirementId, eid=inst.employeeId, s=inst.status, did=inst.documentId, exp=inst.expiryDate)
        return {"id": str(res[0][0])}
    finally:
        if conn: conn.close()

@app.post("/clients/{client_id}/contacts", tags=["Contacts"])
def add_client_contact(client_id: str, contact: Contact, token: str = Depends(get_token)):
    conn = None
    try:
        conn = get_db_connection()
        query = """
            INSERT INTO client_contacts (client_id, contact_type, name, email, phone, is_primary, can_approve_timesheets, can_approve_invoices)
            VALUES (:cid, :type, :name, :email, :phone, :isp, :cat, :cai) RETURNING id
        """
        res = conn.run(query, cid=client_id, type=contact.contactType, name=contact.name, email=contact.email, 
                       phone=contact.phone, isp=contact.isPrimary, cat=contact.canApproveTimesheets, cai=contact.canApproveInvoices)
        return {"id": str(res[0][0])}
    finally:
        if conn: conn.close()

@app.get("/clients/{client_id}/contacts", tags=["Contacts"])
def get_client_contacts_explicit(client_id: str, token: str = Depends(get_token)):
    conn = None
    try:
        conn = get_db_connection()
        rows = conn.run("SELECT * FROM client_contacts WHERE client_id = :id", id=client_id)
        cols = [d['name'] for d in conn.columns]
        return {"contacts": [dict(zip(cols, r)) for r in rows]}
    finally:
        if conn: conn.close()

# --- Employee & Assignment Endpoints ---

@app.get("/employees", tags=["Employees"])
def get_employees(token: str = Depends(get_token)):
    conn = None
    try:
        conn = get_db_connection()
        # Fetch basic employee info
        rows = conn.run("SELECT id, first_name, last_name, email, employee_number, status FROM employees ORDER BY first_name")
        cols = [d['name'] for d in conn.columns]
        employees = []
        for r in rows:
            ed = dict(zip(cols, r))
            employees.append({
                "id": str(ed['id']),
                "firstName": ed['first_name'],
                "lastName": ed['last_name'],
                "email": ed['email'],
                "employeeNumber": ed['employee_number'],
                "status": ed.get('status', 'Active')
            })
        return {"employees": employees}
    finally:
        if conn: conn.close()

@app.get("/clients/{client_id}/projects", tags=["Projects"])
def get_client_projects(client_id: str, token: str = Depends(get_token)):
    conn = None
    try:
        conn = get_db_connection()
        rows = conn.run("SELECT * FROM client_projects WHERE client_id = :id", id=client_id)
        cols = [d['name'] for d in conn.columns]
        projects = []
        for r in rows:
            pd = dict(zip(cols, r))
            projects.append({
                "id": str(pd['id']),
                "clientId": str(pd['client_id']),
                "projectName": pd['project_name'],
                "description": pd.get('description'),
                "startDate": str(pd['start_date']),
                "endDate": str(pd['end_date']) if pd.get('end_date') else None,
                "status": pd.get('status'),
                "budget": float(pd['budget']) if pd.get('budget') else None
            })
        return {"projects": projects}
    finally:
        if conn: conn.close()

@app.post("/clients/{client_id}/projects", tags=["Projects"])
def create_project(client_id: str, project: Project, token: str = Depends(get_token)):
    conn = None
    try:
        conn = get_db_connection()
        query = """
            INSERT INTO client_projects (client_id, project_name, description, start_date, end_date, status, budget, created_at)
            VALUES (:cid, :name, :desc, :start, :end, :stat, :bud, NOW()) RETURNING id
        """
        res = conn.run(query, cid=client_id, name=project.projectName, desc=project.description,
                       start=project.startDate, end=project.endDate, stat=project.status, bud=project.budget)
        return {"id": str(res[0][0]), "message": "Project created"}
    finally:
        if conn: conn.close()

@app.post("/project-assignments", tags=["Assignments"])
def create_assignment(assign: Assignment, token: str = Depends(get_token)):
    conn = None
    try:
        conn = get_db_connection()
        
        # 1. Add to client_employee_assignments (General Link)
        query = """
            INSERT INTO client_employee_assignments (client_id, employee_id, role, status, assignment_date, created_at)
            VALUES (:cid, :eid, :role, :stat, :date, NOW()) RETURNING id
        """
        # If startDate not provided, use today
        start_date = assign.startDate if assign.startDate else "NOW()" 
        
        # Check duplicate
        existing = conn.run("SELECT id FROM client_employee_assignments WHERE client_id=:cid AND employee_id=:eid", cid=assign.clientId, eid=assign.employeeId)
        if existing:
            # Update specific fields if already assigned? Or just ignore. For now, create new entry if role differs maybe? 
            # Or simplified: if exists, we just ensure project is linked.
            assign_id = existing[0][0]
        else:
            if start_date == "NOW()":
                 res = conn.run(query.replace(":date", "NOW()"), cid=assign.clientId, eid=assign.employeeId, role=assign.role, stat=assign.status)
            else:
                 res = conn.run(query, cid=assign.clientId, eid=assign.employeeId, role=assign.role, stat=assign.status, date=start_date)
            assign_id = res[0][0]

        # 2. Add to project_assignments (Specific Project Link) if projectId is present
        if assign.projectId:
            p_query = """
                INSERT INTO client_project_assignments (client_id, employee_id, project_id, role, status, start_date, created_at)
                VALUES (:cid, :eid, :pid, :role, :stat, :date, NOW())
            """
            if start_date == "NOW()":
                 conn.run(p_query.replace(":date", "NOW()"), cid=assign.clientId, eid=assign.employeeId, pid=assign.projectId, role=assign.role, stat=assign.status)
            else:
                 conn.run(p_query, cid=assign.clientId, eid=assign.employeeId, pid=assign.projectId, role=assign.role, stat=assign.status, date=start_date)

        return {"message": "Assignment created successfully", "assignmentId": str(assign_id)}
    finally:
        if conn: conn.close()

@app.get("/project-assignments/client/{client_id}", tags=["Assignments"])
def get_client_assignments(client_id: str, token: str = Depends(get_token)):
    conn = None
    try:
        conn = get_db_connection()
        rows = conn.run("""
            SELECT cea.*, e.first_name, e.last_name, e.email 
            FROM client_employee_assignments cea
            JOIN employees e ON cea.employee_id = e.id
            WHERE cea.client_id = :cid
        """, cid=client_id)
        cols = [d['name'] for d in conn.columns]
        assignments = []
        for r in rows:
            ad = dict(zip(cols, r))
            assignments.append({
                "id": str(ad['id']),
                "employeeId": str(ad['employee_id']),
                "employeeName": f"{ad['first_name']} {ad['last_name']}",
                "role": ad['role'],
                "status": ad['status'],
                "assignmentDate": str(ad['assignment_date'])
            })
        return {"assignments": assignments}
    finally:
        if conn: conn.close()

@app.post("/clients/{client_id}/documents/upload", tags=["Documents"])
async def upload_document_endpoint(
    client_id: str, 
    file: UploadFile = File(...), 
    documentType: str = Form(...),
    token: str = Depends(get_token)
):
    try:
        content = await file.read()
        doc_id, s3_key = upload_to_s3(
            client_id=client_id,
            file_name=file.filename,
            file_content=content,
            content_type=file.content_type,
            doc_type=documentType
        )
        
        if not doc_id:
            raise HTTPException(status_code=500, detail="Failed to upload to S3")
            
        return {
            "message": "Document uploaded successfully",
            "document": {
                "id": doc_id,
                "fileName": file.filename,
                "filePath": s3_key,
                "documentType": documentType
            }
        }
    except Exception as e:
        print(f"Upload Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/documents/{document_id}/download-file", tags=["Documents"])
def get_document_download(document_id: str, token: str = Depends(get_token)):
    conn = None
    try:
        conn = get_db_connection()
        res = conn.run("SELECT * FROM documents WHERE id = :id", id=document_id)
        if not res: raise HTTPException(404, "Document not found")
        cols = [d['name'] for d in conn.columns]
        doc = dict(zip(cols, res[0]))
        
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': doc['bucket_name'], 'Key': doc['file_path']},
            ExpiresIn=3600
        )
        return {
            "url": url,
            "fileName": doc['file_path'].split('/')[-1]
        }
    finally:
        if conn: conn.close()

lambda_handler = Mangum(app)
