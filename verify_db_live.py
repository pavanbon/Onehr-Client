import boto3
import json
import pg8000.native

def test_db():
    secrets_client = boto3.client('secretsmanager', region_name='us-east-2')
    SECRET_NAME = 'rds!db-9888f9d1-be9e-4215-ba07-02fdf234cac4'
    
    try:
        print(f"Fetching secret: {SECRET_NAME}")
        secret = json.loads(secrets_client.get_secret_value(SecretId=SECRET_NAME)['SecretString'])
        
        print("Connecting to DB...")
        conn = pg8000.native.Connection(
            host="hr.cx00uaqeg0tv.us-east-2.rds.amazonaws.com",
            database=secret.get('dbname', 'onehr'),
            user=secret.get('username'),
            password=secret.get('password'),
            port=int(secret.get('port', 5432))
        )
        
        res = conn.run("SELECT version();")
        print(f"Connection Successful! DB Version: {res[0][0]}")
        
        # Check tables
        tables = conn.run("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        print(f"Tables found: {[t[0] for t in tables]}")
        
        conn.close()
        return True
    except Exception as e:
        print(f"DB Test Failed: {e}")
        return False

if __name__ == "__main__":
    test_db()
