import json
import boto3
import pg8000.native
from botocore.exceptions import ClientError

def get_secret():
    secret_name = "rds!db-9888f9d1-be9e-4215-ba07-02fdf234cac4"
    region_name = "us-east-2"
    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager', region_name=region_name)

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        print(f"Error retrieving secret: {e}")
        return None

    if 'SecretString' in get_secret_value_response:
        return json.loads(get_secret_value_response['SecretString'])
    return None

def create_tables():
    secret = get_secret()
    if not secret:
        return

    try:
        conn = pg8000.native.Connection(
            user=secret['username'],
            password=secret['password'],
            host="hr.cx00uaqeg0tv.us-east-2.rds.amazonaws.com",
            database="onehr",
            port=5432
        )
        
        # 1. client_projects
        print("Creating client_projects...")
        conn.run("""
            CREATE TABLE IF NOT EXISTS client_projects (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                client_id UUID NOT NULL, -- references clients(id) implied
                project_name VARCHAR(255) NOT NULL,
                description TEXT,
                start_date DATE NOT NULL,
                end_date DATE,
                status VARCHAR(50) DEFAULT 'Active',
                budget DECIMAL(15, 2),
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            );
        """)

        # 2. client_employee_assignments (Bench/Client level)
        print("Creating client_employee_assignments...")
        conn.run("""
            CREATE TABLE IF NOT EXISTS client_employee_assignments (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                client_id UUID NOT NULL,
                employee_id UUID NOT NULL, -- references employees(id) implied
                role VARCHAR(100),
                status VARCHAR(50) DEFAULT 'Active',
                assignment_date DATE DEFAULT CURRENT_DATE,
                end_date DATE,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            );
        """)

        # 3. client_project_assignments (Specific project level)
        # Note: I am creating a NEW table to avoid conflict with existing 'project_assignments'
        print("Creating client_project_assignments...")
        conn.run("""
            CREATE TABLE IF NOT EXISTS client_project_assignments (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                client_id UUID NOT NULL,
                project_id UUID NOT NULL, -- references client_projects(id)
                employee_id UUID NOT NULL,
                role VARCHAR(100),
                status VARCHAR(50) DEFAULT 'Active',
                start_date DATE DEFAULT CURRENT_DATE,
                end_date DATE,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            );
        """)

        print("Tables created successfully.")
        conn.close()

    except Exception as e:
        print(f"Database error: {e}")

if __name__ == "__main__":
    create_tables()
