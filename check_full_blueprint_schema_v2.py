import boto3
import json
import pg8000.native

def check_comprehensive_schema():
    secrets_client = boto3.client('secretsmanager', region_name='us-east-2')
    SECRET_NAME = 'rds!db-9888f9d1-be9e-4215-ba07-02fdf234cac4'
    
    try:
        secret = json.loads(secrets_client.get_secret_value(SecretId=SECRET_NAME)['SecretString'])
        conn = pg8000.native.Connection(
            host="hr.cx00uaqeg0tv.us-east-2.rds.amazonaws.com",
            database=secret.get('dbname', 'onehr'),
            user=secret.get('username'),
            password=secret.get('password'),
            port=int(secret.get('port', 5432))
        )
        
        tables = [t[0] for t in conn.run("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")]
        
        results = {
            "tables": tables,
            "relevant_columns": []
        }
        
        search_terms = ['client', 'contract', 'po', 'purchase', 'requirement', 'contact', 'addendum']
        query = f"""
            SELECT table_name, column_name 
            FROM information_schema.columns 
            WHERE table_schema = 'public' AND ({ ' OR '.join([f"column_name LIKE '%{term}%' OR table_name LIKE '%{term}%'" for term in search_terms]) })
        """
        relevant = conn.run(query)
        for r in relevant:
            results["relevant_columns"].append({"table": r[0], "column": r[1]})

        with open('schema_results_fixed.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_comprehensive_schema()
