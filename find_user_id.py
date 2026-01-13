import json, boto3, pg8000.native
secret = json.loads(boto3.client('secretsmanager', region_name='us-east-2').get_secret_value(SecretId='rds!db-9888f9d1-be9e-4215-ba07-02fdf234cac4')['SecretString'])

def find_user_id():
    try:
        conn = pg8000.native.Connection(host="hr.cx00uaqeg0tv.us-east-2.rds.amazonaws.com", database="onehr", user=secret['username'], password=secret['password'], port=5432)
        
        # Check for users table
        tables = [r[0] for r in conn.run("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")]
        print(f"Tables: {tables}")
        
        if 'users' in tables:
            res = conn.run("SELECT id FROM users LIMIT 1")
            if res:
                print(f"USER_ID_FOUND:{res[0][0]}")
                return
        
        # If no users table, look at who created existing clients
        res = conn.run("SELECT created_by FROM clients WHERE created_by IS NOT NULL LIMIT 1")
        if res:
            print(f"USER_ID_FOUND:{res[0][0]}")
            return
            
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    find_user_id()
