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

def verify_id(target_id):
    conn = get_db_connection()
    try:
        print(f"--- Verifying Client ID {target_id} ---")
        client = conn.run("SELECT * FROM clients WHERE id = :id", id=target_id)
        if client:
            print(f"Client found: {client[0]}")
        else:
            print("Client NOT found.")

        print(f"\n--- Contacts for Client ID {target_id} ---")
        contacts = conn.run("SELECT * FROM client_contacts WHERE client_id = :id", id=target_id)
        for c in contacts:
            print(c)

        print(f"\n--- Documents for Client ID {target_id} ---")
        docs = conn.run("SELECT * FROM documents WHERE client_id = :id", id=target_id)
        for d in docs:
            print(d)

    finally:
        conn.close()

if __name__ == "__main__":
    verify_id(10)
