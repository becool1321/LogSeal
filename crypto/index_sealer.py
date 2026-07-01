import hashlib
import json
import os
import sqlite3
from datetime import datetime, UTC
from opensearchpy import OpenSearch
from crypto.signer import sign_hash
from security.replay_protection import update_latest_seal

OPENSEARCH_URL = os.getenv("OPENSEARCH_URL", "http://opensearch:9200")
DATABASE_PATH = "instance/logseal.db"

es = OpenSearch(
    hosts=[OPENSEARCH_URL],
    use_ssl=False,
    verify_certs=False
)


def get_today_index():
    return "logs-" + datetime.now(UTC).strftime("%Y-%m-%d")


def create_seal_table():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS seal_metadata (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            index_name TEXT NOT NULL,
            final_hash TEXT NOT NULL,
            total_logs INTEGER NOT NULL,
            seal_timestamp TEXT NOT NULL,
            seal_version INTEGER NOT NULL,
            algorithm TEXT NOT NULL,
            digital_signature TEXT
        )
    """)

    conn.commit()
    conn.close()


def get_next_seal_version(index_name):
    create_seal_table()

    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT MAX(seal_version)
        FROM seal_metadata
        WHERE index_name = ?
    """, (index_name,))

    row = cursor.fetchone()
    conn.close()

    if row and row[0]:
        return row[0] + 1

    return 1


def canonical_log_content(log_source):
    log_data = {
        "user_id": log_source.get("user_id"),
        "username": log_source.get("username"),
        "event_type": log_source.get("event_type"),
        "message": log_source.get("message"),
        "status": log_source.get("status"),
        "timestamp": log_source.get("timestamp")
    }

    return json.dumps(log_data, sort_keys=True)


def generate_hash_chain(index_name):
    target_date = index_name.replace("logs-", "")

    response = es.search(
        index="logs-*",
        body={
            "size": 1000,
            "sort": [
                {
                    "timestamp": {
                        "order": "asc",
                        "unmapped_type": "date"
                    }
                }
            ],
            "query": {
                "range": {
                    "timestamp": {
                        "gte": target_date + "T00:00:00",
                        "lte": target_date + "T23:59:59"
                    }
                }
            }
        },
        ignore_unavailable=True
    )

    logs = response["hits"]["hits"]
    previous_hash = "GENESIS"

    for log in logs:
        log_content = canonical_log_content(log["_source"])

        current_hash = hashlib.sha256(
            (log_content + previous_hash).encode("utf-8")
        ).hexdigest()

        previous_hash = current_hash

    return previous_hash, len(logs)


def save_seal_metadata(index_name, final_hash, total_logs, digital_signature):
    create_seal_table()

    seal_version = get_next_seal_version(index_name)

    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO seal_metadata (
            index_name,
            final_hash,
            total_logs,
            seal_timestamp,
            seal_version,
            algorithm,
            digital_signature
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        index_name,
        final_hash,
        total_logs,
        datetime.now(UTC).isoformat(),
        seal_version,
        "SHA-256_HASH_CHAIN_RSA_SIGNATURE",
        digital_signature
    ))

    conn.commit()
    conn.close()

    return seal_version


def seal_index(index_name=None):
    if index_name is None:
        index_name = get_today_index()

    final_hash, total_logs = generate_hash_chain(index_name)

    digital_signature = sign_hash(final_hash)

    seal_version = save_seal_metadata(
        index_name,
        final_hash,
        total_logs,
        digital_signature
    )

    update_latest_seal(index_name, seal_version)

    print("[SEAL COMPLETE]")
    print(f"Index Name : {index_name}")
    print(f"Total Logs : {total_logs}")
    print(f"Seal Version : {seal_version}")
    print(f"Final Hash : {final_hash}")
    print(f"Signature  : {digital_signature[:50]}...")

    return final_hash
