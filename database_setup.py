"""
Database connection setup and table creation
"""
import os

import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv


load_dotenv()


def _build_db_config() -> dict[str, object]:
    """Build psycopg2 connection args from environment variables."""
    cfg: dict[str, object] = {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": int(os.getenv("DB_PORT", "5432")),
        "database": os.getenv("DB_NAME", "donorcrm_db"),
        "user": os.getenv("DB_USER", "postgres"),
    }
    password = os.getenv("DB_PASSWORD", "").strip()
    if password:
        cfg["password"] = password
    return cfg

def get_connection():
    """Get database connection"""
    return psycopg2.connect(**_build_db_config())

def create_tables():
    """Create database tables"""
    
    # SQL to create tables
    create_tables_sql = """
    -- Drop tables if they exist (for clean slate)
    DROP TABLE IF EXISTS donations CASCADE;
    DROP TABLE IF EXISTS campaigns CASCADE;
    DROP TABLE IF EXISTS donors CASCADE;
    
    -- Create donors table
    CREATE TABLE donors (
        donor_id INTEGER PRIMARY KEY,
        first_name VARCHAR(100),
        last_name VARCHAR(100),
        email VARCHAR(255),
        phone VARCHAR(50),
        address VARCHAR(255),
        city VARCHAR(100),
        state VARCHAR(2),
        zip_code VARCHAR(10),
        created_date DATE,
        donor_type VARCHAR(50)
    );
    
    -- Create campaigns table
    CREATE TABLE campaigns (
        campaign_id INTEGER PRIMARY KEY,
        campaign_name VARCHAR(255),
        start_date DATE,
        end_date DATE,
        goal_amount INTEGER,
        campaign_type VARCHAR(50)
    );
    
    -- Create donations table
    CREATE TABLE donations (
        donation_id INTEGER PRIMARY KEY,
        donor_id INTEGER REFERENCES donors(donor_id),
        campaign_id INTEGER REFERENCES campaigns(campaign_id),
        amount DECIMAL(10, 2),
        donation_date DATE,
        payment_method VARCHAR(50),
        is_recurring BOOLEAN
    );
    
    -- Create indexes for better query performance
    CREATE INDEX idx_donations_donor ON donations(donor_id);
    CREATE INDEX idx_donations_campaign ON donations(campaign_id);
    CREATE INDEX idx_donations_date ON donations(donation_date);
    CREATE INDEX idx_donors_email ON donors(email);
    """
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        print("Creating database tables...")
        print("=" * 50)
        
        # Execute the SQL
        cursor.execute(create_tables_sql)
        conn.commit()
        
        print("Tables created successfully!")
        
        # Verify tables were created
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        
        tables = cursor.fetchall()
        print("\nTables in database:")
        for table in tables:
            print(f"   - {table[0]}")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False

def test_connection():
    """Test database connection"""
    try:
        conn = get_connection()
        print("Successfully connected to PostgreSQL!")
        
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"PostgreSQL version: {version[0][:50]}...")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return False

if __name__ == "__main__":
    print("Testing database connection...")
    print("=" * 50)
    
    if test_connection():
        print("\n")
        create_tables()
    else:
        print("Fix connection issues before creating tables")