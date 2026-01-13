import boto3
import json

def save_creds():
    try:
        client = boto3.client('secretsmanager', region_name='us-east-2')
        secret_value = client.get_secret_value(SecretId='rds!db-9888f9d1-be9e-4215-ba07-02fdf234cac4')
        secret = json.loads(secret_value['SecretString'])
        
        with open("dbeaver_creds.txt", "w") as f:
            f.write("=== DBeaver Connection Details ===\n")
            f.write(f"Host: hr.cx00uaqeg0tv.us-east-2.rds.amazonaws.com\n")
            f.write(f"Port: {secret.get('port', 5432)}\n")
            f.write(f"Database: onehr\n")
            f.write(f"Username: {secret.get('username')}\n")
            f.write(f"Password: {secret.get('password')}\n")
            f.write("==================================\n")
        
        print("Updated credentials with 'onehr' database.")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    save_creds()
