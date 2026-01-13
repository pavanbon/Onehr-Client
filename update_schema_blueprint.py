import boto3
import json
import pg8000.native

def schema_update():
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
        
        # 1. Contracts Table
        conn.run("""
            CREATE TABLE IF NOT EXISTS contracts (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                client_id UUID REFERENCES clients(id) ON DELETE CASCADE,
                title VARCHAR(255) NOT NULL,
                contract_type VARCHAR(100),
                start_date DATE NOT NULL,
                end_date DATE,
                status VARCHAR(50) DEFAULT 'Active',
                document_id UUID,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 2. Addendums Table
        conn.run("""
            CREATE TABLE IF NOT EXISTS contract_addendums (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                contract_id UUID REFERENCES contracts(id) ON DELETE CASCADE,
                title VARCHAR(255) NOT NULL,
                description TEXT,
                document_id UUID,
                signed_date DATE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 3. Requirements Table
        conn.run("""
            CREATE TABLE IF NOT EXISTS client_requirements (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                client_id UUID REFERENCES clients(id) ON DELETE CASCADE,
                title VARCHAR(255) NOT NULL,
                description TEXT,
                category VARCHAR(100), -- e.g. 'Onboarding', 'Compliance'
                is_mandatory BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 4. Requirement Instances (for employees)
        conn.run("""
            CREATE TABLE IF NOT EXISTS requirement_instances (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                requirement_id UUID REFERENCES client_requirements(id) ON DELETE CASCADE,
                employee_id UUID REFERENCES employees(id) ON DELETE CASCADE,
                status VARCHAR(50) DEFAULT 'Pending',
                document_id UUID,
                expiry_date DATE,
                verified_at TIMESTAMP WITH TIME ZONE,
                verified_by UUID,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 5. Client Portal Users
        conn.run("""
            CREATE TABLE IF NOT EXISTS client_portal_users (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                client_id UUID REFERENCES clients(id) ON DELETE CASCADE,
                email VARCHAR(255) UNIQUE NOT NULL,
                role VARCHAR(100) DEFAULT 'Admin',
                is_active BOOLEAN DEFAULT TRUE,
                last_login TIMESTAMP WITH TIME ZONE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 6. Update PO table to link to Contract instead of just Client (optional but good practice)
        # Check if contract_id column exists
        cols = conn.run("SELECT column_name FROM information_schema.columns WHERE table_name = 'purchase_orders' AND column_name = 'contract_id'")
        if not cols:
             conn.run("ALTER TABLE purchase_orders ADD COLUMN contract_id UUID REFERENCES contracts(id) ON DELETE SET NULL")

        print("Tables created successfully!")
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    schema_update()
