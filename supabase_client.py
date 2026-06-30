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

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

logger = logging.getLogger(__name__)

def get_supabase():
    """Get Supabase client instance"""
    return supabase

def test_connection():
    """Test the Supabase connection"""
    try:
        # Test connection by fetching a single user
        response = supabase.table('users').select('*').limit(1).execute()
        logger.info("✅ Supabase connection successful!")
        return True
    except Exception as e:
        logger.error(f"❌ Supabase connection failed: {str(e)}")
        return False