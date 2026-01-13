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

def cleanup():
    conn = get_db_connection()
    try:
        print("Cleaning up test records (IDs > 8)...")
        # Delete related records first
        conn.run("DELETE FROM documents WHERE client_id > 8")
        conn.run("DELETE FROM client_contacts WHERE client_id > 8")
        conn.run("DELETE FROM clients WHERE id > 8")
        print("Cleanup complete.")
    finally:
        conn.close()

if __name__ == "__main__":
    cleanup()
