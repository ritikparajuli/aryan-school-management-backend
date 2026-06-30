# test_supabase.py
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
print(f"Testing connection...")

# Try different IPs
ips = [
    "185.38.109.200",
    "185.38.109.201", 
    "185.38.109.202",
    "185.38.109.203",
]

for ip in ips:
    try:
        # Replace hostname with IP
        test_url = DATABASE_URL.replace(
            "db.rmulwbdlbclwsidovrcd.supabase.co",
            ip
        )
        print(f"\nTrying IP: {ip}")
        engine = create_engine(test_url, connect_args={"connect_timeout": 5})
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print(f"✅ SUCCESS with IP: {ip}")
            print(f"   Use this IP in your DATABASE_URL")
            break
    except Exception as e:
        print(f"❌ Failed with {ip}: {str(e)[:100]}")