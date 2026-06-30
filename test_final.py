# test_final.py
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

print("=" * 50)
print("Testing Supabase Connection")
print("=" * 50)
print(f"Using URL: {DATABASE_URL[:50]}...")
print("-" * 50)

try:
    conn = psycopg2.connect(DATABASE_URL)
    print("✅ CONNECTION SUCCESSFUL! 🎉")
    
    cur = conn.cursor()
    cur.execute("SELECT version();")
    version = cur.fetchone()
    print(f"✅ PostgreSQL Version: {version[0][:60]}...")
    
    # Check existing tables
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        ORDER BY table_name;
    """)
    tables = cur.fetchall()
    print(f"\n📊 Tables in your database: {len(tables)}")
    if tables:
        for table in tables[:10]:  # Show first 10
            print(f"   - {table[0]}")
        if len(tables) > 10:
            print(f"   ... and {len(tables) - 10} more")
    else:
        print("   (No tables found - you need to create them)")
    
    cur.close()
    conn.close()
    print("\n✅ All tests passed! Your connection is working.")
    print("\n📝 Next step: Create your tables")
    
except Exception as e:
    print(f"❌ CONNECTION FAILED!")
    print(f"Error: {e}")