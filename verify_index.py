from datetime import datetime, UTC
from crypto.index_verifier import verify_index

index_name = "logs-" + datetime.now(UTC).strftime("%Y-%m-%d")

verify_index(index_name)
