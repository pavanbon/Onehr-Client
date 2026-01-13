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

def upgrade_docs():
    conn = get_db_connection()
    try:
        print("Upgrading client_documents table...")
        
        # Add status column
        try:
            conn.run("ALTER TABLE client_documents ADD COLUMN status TEXT DEFAULT 'Pending'")
            print("Added status column")
        except Exception as e:
            if "already exists" in str(e):
                print("status column already exists")
            else:
                print(f"Error adding status: {e}")

        # Add external_id column (for documentId)
        try:
            conn.run("ALTER TABLE client_documents ADD COLUMN external_id TEXT")
            print("Added external_id column")
        except Exception as e:
            if "already exists" in str(e):
                print("external_id column already exists")
            else:
                print(f"Error adding external_id: {e}")

        # Make file_path nullable (if possible, this is dialect specific, usually ALTER COLUMN ... DROP NOT NULL)
        try:
            conn.run("ALTER TABLE client_documents ALTER COLUMN file_path DROP NOT NULL")
            print("Made file_path nullable")
        except Exception as e:
            print(f"Error making file_path nullable (might already be): {e}")

    finally:
        conn.close()

if __name__ == "__main__":
    upgrade_docs()
