import json
import boto3

SECRET_NAME = 'rds!db-9888f9d1-be9e-4215-ba07-02fdf234cac4'
secrets_client = boto3.client('secretsmanager', region_name='us-east-2')

def check_secret_details():
    try:
        secret = json.loads(secrets_client.get_secret_value(SecretId=SECRET_NAME)['SecretString'])
        print(f"DATABASE NAME IN SECRET: {secret.get('dbname')}")
        print(f"USERNAME IN SECRET: {secret.get('username')}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_secret_details()
