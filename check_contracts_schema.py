import boto3
import json
import pg8000.native

def check_schema():
    secrets_client = boto3.client('secretsmanager', region_name='us-east-2')
    SECRET_NAME = 'rds!db-9888f9d1-be9e-4215-ba07-02fdf234cac4'
    
    try:
        secret = json.loads(secrets_client.get_secret_value(SecretId=SECRET_NAME)['SecretString'])
        conn = pg8000.native.Connection(
            host="hr.cx00uaqeg0tv.us-east-2.rds.amazonaws.com",
            database=secret.get('dbname', 'onehr'),
            user=secret.get('username'),
            password=secret.get('password'),
            port=int(secret.get('port', 5432))
        )
        
        # Check all tables
        tables = conn.run("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        print("Existing Tables:")
        for t in tables:
            print(f"- {t[0]}")
            
        # Check for any "contract" columns in any table
        print("\nSearching for 'contract' in columns:")
        contract_cols = conn.run("""
            SELECT table_name, column_name 
            FROM information_schema.columns 
            WHERE table_schema = 'public' AND (column_name LIKE '%contract%' OR table_name LIKE '%contract%')
        """)
        for tc in contract_cols:
            print(f"Table: {tc[0]}, Column: {tc[1]}")

        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_schema()
