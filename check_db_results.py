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
        print("\n" + "="*50)
        print("          ONEHR DATABASE RECENT RECORDS")
        print("="*50)
        
        clients = conn.run("SELECT id, legal_name, company_name, created_at FROM clients ORDER BY created_at DESC LIMIT 3")
        for c in clients:
            print(f"\n[CLIENT ID: {c[0]}]")
            print(f"Name      : {c[1]}")
            print(f"Company   : {c[2]}")
            print(f"Created At: {c[3]}")
            
            # Show contacts
            contacts = conn.run("SELECT name, email FROM client_contacts WHERE client_id = :cid", cid=c[0])
            if contacts:
                print("  -> Contacts:")
                for con in contacts:
                    print(f"     - {con[0]} ({con[1]})")
            
            # Show documents
            docs = conn.run("SELECT doc_type, status FROM documents WHERE client_id = :cid", cid=c[0])
            if docs:
                print("  -> Documents:")
                for d in docs:
                    print(f"     - {d[0]} (Status: {d[1]})")
            print("-" * 50)

    except Exception as e:
        print(f"Error fetching data: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    view_my_data()
