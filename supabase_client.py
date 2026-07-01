# supabase_client.py
import os
from supabase import create_client, Client
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Get Supabase credentials from .env
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

# Initialize Supabase client with anon key (for public operations)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Initialize Supabase admin client with service role key (bypasses RLS)
supabase_admin: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

logger = logging.getLogger(__name__)

def get_supabase():
    """Get Supabase client instance"""
    return supabase

def get_supabase_admin():
    """Get Supabase admin client instance (bypasses RLS)"""
    return supabase_admin

def test_connection():
    """Test the Supabase connection"""
    try:
        # Test connection by fetching a single user using admin client
        response = supabase_admin.table('users').select('*').limit(1).execute()
        logger.info("✅ Supabase connection successful!")
        return True
    except Exception as e:
        logger.error(f"❌ Supabase connection failed: {str(e)}")
        return False