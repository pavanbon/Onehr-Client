import lambda_function
import sys

def check_tables():
    print("Attempting to connect to the database to list tables...")
    try:
        conn = lambda_function.get_db_connection()
        cursor = conn.cursor()
        
        # Query for specific tables
        target_tables = ['clients', 'client_contacts', 'documents']
        
        print("\nChecking for required tables:")
        for table in target_tables:
            cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = %s);", (table,))
            exists = cursor.fetchone()[0]
            status = "EXISTS" if exists else "MISSING"
            print(f" - {table}: {status}")

        # List ALL tables just in case
        print("\nListing ALL tables in public schema:")
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
        all_tables = cursor.fetchall()
        if not all_tables:
            print(" (No tables found)")
        for t in all_tables:
            print(f" - {t[0]}")
            
        conn.close()
        
    except Exception as e:
        print(f"\n[!] Connection Failed: {str(e)}")
        print("Note: If you see a timeout, it likely means your IP is blocked by the AWS RDS Security Group.")

if __name__ == "__main__":
    check_tables()
