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

def view_my_data():
    conn = get_db_connection()
    try:
        # Check available columns in client_contacts
        print("Checking client_contacts columns...")
        cols = conn.run("SELECT column_name FROM information_schema.columns WHERE table_name='client_contacts'")
        col_names = [c[0] for c in cols]
        print(f"Available columns: {col_names}")

        print("\n=== LATEST CLIENTS ===")
        clients = conn.run("SELECT id, legal_name, company_name, created_at FROM clients ORDER BY created_at DESC LIMIT 5")
        for c in clients:
            print(f"ID: {c[0]} | Name: {c[1]} | Created: {c[3]}")
            
            # Show contacts for this client
            print("  -> Contacts:")
            # Use only available columns
            query_cols = []
            if 'name' in col_names: query_cols.append('name')
            if 'email' in col_names: query_cols.append('email')
            if 'role' in col_names: query_cols.append('role')
            if 'contact_type' in col_names: query_cols.append('contact_type')
            
            if query_cols:
                contacts = conn.run(f"SELECT {', '.join(query_cols)} FROM client_contacts WHERE client_id = :cid", cid=c[0])
                for con in contacts:
                    print(f"     - {', '.join([str(val) for val in con])}")
            
            # Show documents for this client
            print("  -> Documents:")
            docs = conn.run("SELECT doc_type, status FROM documents WHERE client_id = :cid", cid=c[0])
            for d in docs:
                print(f"     - {d[0]} (Status: {d[1]})")
            print("-" * 30)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    view_my_data()
