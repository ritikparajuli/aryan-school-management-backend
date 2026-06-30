# test_supabase_api.py
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

print("=" * 60)
print("Testing Supabase API Connection")
print("=" * 60)
print(f"URL: {SUPABASE_URL}")
print(f"Key: {SUPABASE_KEY[:20]}...")
print("-" * 60)

try:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # Test connection by fetching users
    print("\n📊 Fetching users...")
    response = supabase.table('users').select('*').limit(5).execute()
    
    print("✅ Supabase API connection successful!")
    print(f"✅ Found {len(response.data)} users")
    
    if response.data:
        print("\n📊 Sample users:")
        for user in response.data:
            print(f"   - ID: {user.get('id')}, Email: {user.get('email')}, Role: {user.get('role')}")
    
    print("\n" + "=" * 60)
    print("✅ All tests passed! Your API keys are working.")
    print("You can now start your backend: python main.py")
    
except Exception as e:
    print(f"\n❌ Connection failed: {str(e)}")
    print("\n💡 Troubleshooting:")
    print("1. Check SUPABASE_URL in .env")
    print("2. Check SUPABASE_KEY in .env")
    print("3. Make sure you installed: pip install supabase")