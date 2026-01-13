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

def fix_documents_table():
    conn = get_db_connection()
    try:
        # 1. Check if documents table exists
        res = conn.run("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'documents')")
        docs_exists = res[0][0]
        print(f"documents table exists: {docs_exists}")
        
        if docs_exists:
            # Check for client_id column
            res = conn.run("SELECT EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'documents' AND column_name = 'client_id')")
            cid_exists = res[0][0]
            print(f"client_id exists in documents: {cid_exists}")
            
            if not cid_exists:
                print("Adding client_id to documents...")
                conn.run("ALTER TABLE documents ADD COLUMN client_id INTEGER") # Or UUID? Let's check clients table ID type

            # Check for status column
            res = conn.run("SELECT EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'documents' AND column_name = 'status')")
            status_exists = res[0][0]
            print(f"status exists in documents: {status_exists}")
            
            if not status_exists:
                print("Adding status to documents...")
                conn.run("ALTER TABLE documents ADD COLUMN status TEXT DEFAULT 'Pending'")

        # 2. Check clients ID type
        res = conn.run("SELECT data_type FROM information_schema.columns WHERE table_name = 'clients' AND column_name = 'id'")
        print(f"Clients ID type: {res[0][0]}")

    finally:
        conn.close()

if __name__ == "__main__":
    fix_documents_table()
