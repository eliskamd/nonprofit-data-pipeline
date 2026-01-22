"""
Load CSV data into PostgreSQL database
"""
import pandas as pd
import psycopg2
from psycopg2.extras import execute_batch
import sys

# Database connection parameters
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'donorcrm_db',
    'user': 'postgres',
    'password': 'admin'
}

def get_connection():
    """Get database connection"""
    return psycopg2.connect(**DB_CONFIG)

def load_donors():
    """Load donors from CSV to database"""
    print("\n📊 Loading donors...")
    
    try:
        # Read CSV
        df = pd.read_csv('data/synthetic/donors.csv')
        print(f"   Read {len(df)} donors from CSV")
        
        # Connect to database
        conn = get_connection()
        cursor = conn.cursor()
        
        # Prepare INSERT statement
        insert_sql = """
            INSERT INTO donors (
                donor_id, first_name, last_name, email, phone,
                address, city, state, zip_code, created_date, donor_type
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        # Convert DataFrame to list of tuples
        records = [
            (
                row['donor_id'], row['first_name'], row['last_name'], 
                row['email'], row['phone'], row['address'], row['city'],
                row['state'], row['zip_code'], row['created_date'], 
                row['donor_type']
            )
            for _, row in df.iterrows()
        ]
        
        # Batch insert for performance
        execute_batch(cursor, insert_sql, records, page_size=100)
        conn.commit()
        
        # Verify count
        cursor.execute("SELECT COUNT(*) FROM donors")
        count = cursor.fetchone()[0]
        print(f"   ✅ Loaded {count} donors into database")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"   ❌ Error loading donors: {e}")
        return False

def load_campaigns():
    """Load campaigns from CSV to database"""
    print("\n📢 Loading campaigns...")
    
    try:
        # Read CSV
        df = pd.read_csv('data/synthetic/campaigns.csv')
        print(f"   Read {len(df)} campaigns from CSV")
        
        # Connect to database
        conn = get_connection()
        cursor = conn.cursor()
        
        # Prepare INSERT statement
        insert_sql = """
            INSERT INTO campaigns (
                campaign_id, campaign_name, start_date, end_date,
                goal_amount, campaign_type
            ) VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        # Convert DataFrame to list of tuples
        records = [
            (
                row['campaign_id'], row['campaign_name'], 
                row['start_date'], row['end_date'],
                row['goal_amount'], row['campaign_type']
            )
            for _, row in df.iterrows()
        ]
        
        # Batch insert
        execute_batch(cursor, insert_sql, records, page_size=100)
        conn.commit()
        
        # Verify count
        cursor.execute("SELECT COUNT(*) FROM campaigns")
        count = cursor.fetchone()[0]
        print(f"   ✅ Loaded {count} campaigns into database")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"   ❌ Error loading campaigns: {e}")
        return False

def load_donations():
    """Load donations from CSV to database"""
    print("\n💰 Loading donations...")
    
    try:
        # Read CSV
        df = pd.read_csv('data/synthetic/donations.csv')
        print(f"   Read {len(df)} donations from CSV")
        
        # Connect to database
        conn = get_connection()
        cursor = conn.cursor()
        
        # Prepare INSERT statement
        insert_sql = """
            INSERT INTO donations (
                donation_id, donor_id, campaign_id, amount,
                donation_date, payment_method, is_recurring
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        
        # Convert DataFrame to list of tuples
        records = [
            (
                row['donation_id'], row['donor_id'], row['campaign_id'],
                row['amount'], row['donation_date'], row['payment_method'],
                row['is_recurring']
            )
            for _, row in df.iterrows()
        ]
        
        # Batch insert
        execute_batch(cursor, insert_sql, records, page_size=100)
        conn.commit()
        
        # Verify count
        cursor.execute("SELECT COUNT(*) FROM donations")
        count = cursor.fetchone()[0]
        print(f"   ✅ Loaded {count} donations into database")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"   ❌ Error loading donations: {e}")
        return False

def verify_data():
    """Run some queries to verify data loaded correctly"""
    print("\n🔍 Verifying data...")
    print("=" * 50)
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Total counts
        cursor.execute("SELECT COUNT(*) FROM donors")
        donor_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM campaigns")
        campaign_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM donations")
        donation_count = cursor.fetchone()[0]
        
        print(f"📊 Record counts:")
        print(f"   • Donors: {donor_count:,}")
        print(f"   • Campaigns: {campaign_count}")
        print(f"   • Donations: {donation_count:,}")
        
        # Total donation amount
        cursor.execute("SELECT SUM(amount) FROM donations")
        total_amount = cursor.fetchone()[0]
        print(f"\n💵 Total donations: ${total_amount:,.2f}")
        
        # Average donation
        cursor.execute("SELECT AVG(amount) FROM donations")
        avg_amount = cursor.fetchone()[0]
        print(f"💵 Average donation: ${avg_amount:.2f}")
        
        # Sample donor with donations
        cursor.execute("""
            SELECT 
                d.first_name, 
                d.last_name, 
                COUNT(don.donation_id) as num_donations,
                SUM(don.amount) as total_given
            FROM donors d
            LEFT JOIN donations don ON d.donor_id = don.donor_id
            GROUP BY d.donor_id, d.first_name, d.last_name
            HAVING COUNT(don.donation_id) > 0
            ORDER BY total_given DESC
            LIMIT 5
        """)
        
        print(f"\n🌟 Top 5 donors by total amount:")
        for row in cursor.fetchall():
            print(f"   • {row[0]} {row[1]}: {row[2]} donations, ${row[3]:,.2f} total")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error verifying data: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting data load process...")
    print("=" * 50)
    
    # Load data in order (donors and campaigns first, then donations)
    success = True
    
    if not load_donors():
        success = False
    
    if not load_campaigns():
        success = False
    
    if success and not load_donations():
        success = False
    
    if success:
        verify_data()
        print("\n" + "=" * 50)
        print("✅ DATA LOAD COMPLETE!")
        print("=" * 50)
    else:
        print("\n⚠️  Some data failed to load. Check errors above.")
        sys.exit(1)