from datetime import datetime, UTC
from crypto.index_verifier import verify_index

index_name = "logs-" + datetime.now(UTC).strftime("%Y-%m-%d")

print("=" * 60)
print(f"[AUTOMATED VERIFICATION] {datetime.now(UTC).isoformat()}")
print(f"Index: {index_name}")

result = verify_index(index_name)

print(f"Status: {result.get('status')}")
print(f"Message: {result.get('message')}")
print(f"Total Logs: {result.get('total_logs')}")
print("=" * 60)
