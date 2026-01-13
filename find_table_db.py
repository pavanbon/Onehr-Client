import json
import boto3
import pg8000.native

SECRET_NAME = 'rds!db-9888f9d1-be9e-4215-ba07-02fdf234cac4'
secrets_client = boto3.client('secretsmanager', region_name='us-east-2')

def get_db_connection(dbname):
    secret = json.loads(secrets_client.get_secret_value(SecretId=SECRET_NAME)['SecretString'])
    conn = pg8000.native.Connection(
        host="hr.cx00uaqeg0tv.us-east-2.rds.amazonaws.com",
        database=dbname,
        user=secret.get('username'),
        password=secret.get('password'),
        port=int(secret.get('port', 5432))
    )
    return conn

def find_table():
    for db in ["postgres", "onehr"]:
        try:
            conn = get_db_connection(db)
            res = conn.run("SELECT count(*) FROM clients")
            print(f"Database '{db}' has {res[0][0]} clients.")
            conn.close()
        except Exception as e:
            print(f"Database '{db}' error: {e}")

if __name__ == "__main__":
    find_table()
