from datetime import datetime, UTC
from crypto.index_sealer import seal_index

index_name = "logs-" + datetime.now(UTC).strftime("%Y-%m-%d")

print("=" * 60)
print(f"[AUTOMATED DAILY SEAL] {datetime.now(UTC).isoformat()}")
print(f"Index: {index_name}")

final_hash = seal_index(index_name)

print(f"Final Hash: {final_hash}")
print("=" * 60)
