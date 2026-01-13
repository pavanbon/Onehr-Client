import json
import boto3
import pg8000.native

SECRET_NAME = 'rds!db-9888f9d1-be9e-4215-ba07-02fdf234cac4'
secrets_client = boto3.client('secretsmanager', region_name='us-east-2')

def get_db_connection():
    secret = json.loads(secrets_client.get_secret_value(SecretId=SECRET_NAME)['SecretString'])
    conn = pg8000.native.Connection(
        host="hr.cx00uaqeg0tv.us-east-2.rds.amazonaws.com",
        database=secret.get('dbname', 'postgres'),
        user=secret.get('username'),
        password=secret.get('password'),
        port=int(secret.get('port', 5432))
    )
    return conn

def upgrade_schema():
    conn = get_db_connection()
    try:
        print("Adding new columns to clients table...")
        # Add columns if they don't exist
        columns_to_add = [
            ("address_street", "TEXT"),
            ("address_street2", "TEXT"),
            ("address_city", "TEXT"),
            ("address_state", "TEXT"),
            ("address_zip", "TEXT"),
            ("billing_address_street", "TEXT"),
            ("billing_address_street2", "TEXT"),
            ("billing_address_city", "TEXT"),
            ("billing_address_state", "TEXT"),
            ("billing_address_zip", "TEXT"),
            ("same_as_business_address", "BOOLEAN DEFAULT TRUE"),
            ("is_existing_client", "BOOLEAN DEFAULT FALSE"),
            ("requires_full_onboarding", "BOOLEAN DEFAULT TRUE"),
            ("onboarding_status", "TEXT DEFAULT 'not-started'"),
            ("has_compliance_issues", "BOOLEAN DEFAULT FALSE"),
            ("has_expiring_pos", "BOOLEAN DEFAULT FALSE"),
            ("has_expiring_documents", "BOOLEAN DEFAULT FALSE"),
            ("can_generate_invoices", "BOOLEAN DEFAULT FALSE"),
            ("contract_signed", "BOOLEAN DEFAULT FALSE"),
            ("documents_complete", "BOOLEAN DEFAULT FALSE"),
            ("active_engagements", "INTEGER DEFAULT 0"),
            ("total_engagement_value", "NUMERIC DEFAULT 0.0")
        ]
        
        for col_name, col_type in columns_to_add:
            try:
                conn.run(f"ALTER TABLE clients ADD COLUMN {col_name} {col_type}")
                print(f"Added {col_name}")
            except Exception as e:
                if "already exists" in str(e):
                    print(f"Column {col_name} already exists, skipping.")
                else:
                    print(f"Error adding {col_name}: {e}")
        
        print("Schema upgrade complete.")
    finally:
        conn.close()

if __name__ == "__main__":
    upgrade_schema()
