import json
import boto3
import pg8000.native
from botocore.exceptions import ClientError

def get_secret():
    secret_name = "rds!db-9888f9d1-be9e-4215-ba07-02fdf234cac4"
    region_name = "us-east-2"
    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager', region_name=region_name)

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        print(f"Error retrieving secret: {e}")
        return None

    if 'SecretString' in get_secret_value_response:
        return json.loads(get_secret_value_response['SecretString'])
    return None

def inspect_tables():
    secret = get_secret()
    if not secret:
        return

    try:
        conn = pg8000.native.Connection(
            user=secret['username'],
            password=secret['password'],
            host="hr.cx00uaqeg0tv.us-east-2.rds.amazonaws.com",
            database="onehr",
            port=5432
        )
        
        for table in ['projects', 'project_assignments', 'client_employee_assignments', 'client_projects']:
            print(f"\n--- {table} ---")
            try:
                rows = conn.run(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{table}'")
                if not rows:
                    print("Table does not exist.")
                else:
                    for r in rows:
                        print(f"{r[0]}: {r[1]}")
            except Exception as e:
                print(e)
            
        conn.close()

    except Exception as e:
        print(f"Database error: {e}")

if __name__ == "__main__":
    inspect_tables()
