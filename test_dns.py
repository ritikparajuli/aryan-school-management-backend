# test_dns.py
import socket

domains = [
    "db.rmulwbdlbclwsidovrcd.supabase.co",
    "aws-0-ap-southeast-1.pooler.supabase.com",
]

print("Testing DNS Resolution:")
print("-" * 50)

for domain in domains:
    try:
        print(f"\nResolving: {domain}")
        ip = socket.gethostbyname(domain)
        print(f"✅ IP Address: {ip}")
    except Exception as e:
        print(f"❌ Failed: {e}")

print("\n" + "-" * 50)
print("Try pinging the domain:")
print(f"ping db.rmulwbdlbclwsidovrcd.supabase.co")