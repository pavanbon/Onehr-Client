import json, boto3, pg8000.native
secret = json.loads(boto3.client('secretsmanager', region_name='us-east-2').get_secret_value(SecretId='rds!db-9888f9d1-be9e-4215-ba07-02fdf234cac4')['SecretString'])
conn = pg8000.native.Connection(host="hr.cx00uaqeg0tv.us-east-2.rds.amazonaws.com", database="postgres", user=secret['username'], password=secret['password'], port=5432)

# Find the latest client
res = conn.run("SELECT id, legal_name FROM clients ORDER BY created_at DESC LIMIT 1")
if res:
    client_id = res[0][0]
    client_name = res[0][1]
    print(f"Updating client '{client_name}' (ID: {client_id})...")
    conn.run("UPDATE clients SET industry = 'Healthcare LLC' WHERE id = :id", id=client_id)
    print("SUCCESS: Industry updated to 'Healthcare LLC'.")
else:
    print("No clients found.")
conn.close()
