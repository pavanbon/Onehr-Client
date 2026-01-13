import json, boto3, pg8000.native
secret = json.loads(boto3.client('secretsmanager', region_name='us-east-2').get_secret_value(SecretId='rds!db-9888f9d1-be9e-4215-ba07-02fdf234cac4')['SecretString'])
conn = pg8000.native.Connection(host="hr.cx00uaqeg0tv.us-east-2.rds.amazonaws.com", database="postgres", user=secret['username'], password=secret['password'], port=5432)

res = conn.run("SELECT * FROM clients ORDER BY created_at DESC LIMIT 1")
cols = [d['name'] for d in conn.columns]
data = dict(zip(cols, res[0]))
print(json.dumps(data, indent=2, default=str))
conn.close()
