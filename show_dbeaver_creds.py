import boto3
import json

def show_creds():
    try:
        client = boto3.client('secretsmanager', region_name='us-east-2')
        secret_value = client.get_secret_value(SecretId='rds!db-9888f9d1-be9e-4215-ba07-02fdf234cac4')
        secret = json.loads(secret_value['SecretString'])
        
        print("\n=== DBeaver Connection Details ===")
        print(f"Host:     hr.cx00uaqeg0tv.us-east-2.rds.amazonaws.com")
        print(f"Port:     {secret.get('port', 5432)}")
        print(f"Database: {secret.get('dbname', 'postgres')}")
        print(f"Username: {secret.get('username')}")
        print(f"Password: {secret.get('password')}")
        print("==================================\n")
        
    except Exception as e:
        print(f"Error retrieving credentials: {e}")

if __name__ == "__main__":
    show_creds()
