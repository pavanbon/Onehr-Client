import json, boto3, pg8000.native
secret = json.loads(boto3.client('secretsmanager', region_name='us-east-2').get_secret_value(SecretId='rds!db-9888f9d1-be9e-4215-ba07-02fdf234cac4')['SecretString'])
conn = pg8000.native.Connection(host="hr.cx00uaqeg0tv.us-east-2.rds.amazonaws.com", database="postgres", user=secret['username'], password=secret['password'], port=5432)

res = conn.run("SELECT id, legal_name, company_name, industry FROM clients ORDER BY created_at DESC LIMIT 1")
print(f"ID: {res[0][0]}")
print(f"Legal Name: {res[0][1]}")
print(f"Company Name: {res[0][2]}")
print(f"Industry: {res[0][3]}")
conn.close()
