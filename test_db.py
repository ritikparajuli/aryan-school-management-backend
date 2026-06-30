# test_db.py
import psycopg2
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

print("=" * 50)
print("Testing Supabase Connection")
print("=" * 50)
print(f"Connecting to: db.rmulwbdlbclwsidovrcd.supabase.co:5432")
print("-" * 50)

try:
    conn = psycopg2.connect(DATABASE_URL)
    print("✅ CONNECTION SUCCESSFUL! 🎉")
    
    cur = conn.cursor()
    cur.execute("SELECT version();")
    version = cur.fetchone()
    print(f"✅ PostgreSQL Version: {version[0][:60]}...")
    
    # Check if your tables exist
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        ORDER BY table_name;
    """)
    tables = cur.fetchall()
    print(f"\n📊 Tables in your database: {len(tables)}")
    if tables:
        for table in tables:
            print(f"   - {table[0]}")
    else:
        print("   (No tables found - you may need to create them)")
    
    cur.close()
    conn.close()
    print("\n✅ All tests passed!")
    
except Exception as e:
    print(f"❌ CONNECTION FAILED!")
    print(f"Error: {e}")