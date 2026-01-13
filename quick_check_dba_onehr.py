import json, boto3, pg8000.native
secret = json.loads(boto3.client('secretsmanager', region_name='us-east-2').get_secret_value(SecretId='rds!db-9888f9d1-be9e-4215-ba07-02fdf234cac4')['SecretString'])
conn = pg8000.native.Connection(host="hr.cx00uaqeg0tv.us-east-2.rds.amazonaws.com", database="onehr", user=secret['username'], password=secret['password'], port=5432)
cols = [r[0] for r in conn.run("SELECT column_name FROM information_schema.columns WHERE table_name='clients'")]
print("doing_business_as" in cols)
print("dba_name" in cols)
conn.close()
