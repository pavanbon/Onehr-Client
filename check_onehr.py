import boto3
import json
import pg8000.native

def check_onehr_db():
    try:
        client = boto3.client('secretsmanager', region_name='us-east-2')
        secret_value = client.get_secret_value(SecretId='rds!db-9888f9d1-be9e-4215-ba07-02fdf234cac4')
        secret = json.loads(secret_value['SecretString'])
        
        print("\n=== Testing Connection to 'onehr' ===")
        conn = pg8000.native.Connection(
            host="hr.cx00uaqeg0tv.us-east-2.rds.amazonaws.com",
            database="onehr",
            user=secret.get('username'),
            password=secret.get('password'),
            port=5432
        )
        print("SUCCESS: Connected to 'onehr' database.")
        conn.close()
        
    except Exception as e:
        print(f"FAILED: Could not connect to 'onehr'. Error: {e}")

if __name__ == "__main__":
    check_onehr_db()
