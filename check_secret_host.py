import lambda_function
import json

def check_secret():
    try:
        response = lambda_function.secrets_client.get_secret_value(
            SecretId=lambda_function.SECRET_NAME
        )
        secret = json.loads(response['SecretString'])
        host = secret.get('host')
        print(f"Host in secret: {host}")
    except Exception as e:
        print(f"Error reading secret: {e}")

if __name__ == "__main__":
    check_secret()
