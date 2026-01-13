import json, boto3, pg8000.native
secret = json.loads(boto3.client('secretsmanager', region_name='us-east-2').get_secret_value(SecretId='rds!db-9888f9d1-be9e-4215-ba07-02fdf234cac4')['SecretString'])

def check_db(name):
    print(f"\n--- Checking DB: {name} ---")
    try:
        conn = pg8000.native.Connection(host="hr.cx00uaqeg0tv.us-east-2.rds.amazonaws.com", database=name, user=secret['username'], password=secret['password'], port=5432)
        cols = [r[0] for r in conn.run("SELECT column_name FROM information_schema.columns WHERE table_name='clients'")]
        print(f"Columns: {sorted(cols)}")
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

check_db("postgres")
check_db("onehr")
