import json, boto3, pg8000.native
secret = json.loads(boto3.client('secretsmanager', region_name='us-east-2').get_secret_value(SecretId='rds!db-9888f9d1-be9e-4215-ba07-02fdf234cac4')['SecretString'])
conn = pg8000.native.Connection(host="hr.cx00uaqeg0tv.us-east-2.rds.amazonaws.com", database="postgres", user=secret['username'], password=secret['password'], port=5432)
res = conn.run("SELECT id, legal_name, industry FROM clients ORDER BY created_at DESC LIMIT 5")
for r in res:
    print(f"ID: {r[0]} | Name: {r[1]} | Industry: {r[2]}")
conn.close()
