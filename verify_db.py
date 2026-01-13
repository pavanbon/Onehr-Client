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

def check_recent_clients():
    conn = get_db_connection()
    try:
        print("Checking most recent clients...")
        rows = conn.run("SELECT id, legal_name, created_at FROM clients ORDER BY created_at DESC LIMIT 5")
        for row in rows:
            print(f"ID: {row[0]}, Name: {row[1]}, Created At: {row[2]}")
        
        print("\nChecking most recent contacts...")
        rows = conn.run("SELECT id, client_id, name FROM client_contacts ORDER BY id DESC LIMIT 5")
        for row in rows:
            print(f"ID: {row[0]}, Client ID: {row[1]}, Name: {row[2]}")

        print("\nChecking most recent documents...")
        rows = conn.run("SELECT id, client_id, doc_type, status FROM documents ORDER BY id DESC LIMIT 5")
        for row in rows:
            print(f"ID: {row[0]}, Client ID: {row[1]}, Type: {row[2]}, Status: {row[3]}")

    finally:
        conn.close()

if __name__ == "__main__":
    check_recent_clients()
