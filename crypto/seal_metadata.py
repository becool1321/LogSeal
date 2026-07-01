import sqlite3

DATABASE_PATH = "instance/logseal.db"


def show_all_seals():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            index_name,
            final_hash,
            total_logs,
            seal_timestamp,
            seal_version,
            algorithm,
            digital_signature
        FROM seal_metadata
        ORDER BY id DESC
    """)

    seals = cursor.fetchall()
    conn.close()

    if not seals:
        print("[NO SEALS FOUND]")
        return

    print("\n[SEAL METADATA RECORDS]\n")

    for seal in seals:
        print(f"ID                : {seal[0]}")
        print(f"Index Name        : {seal[1]}")
        print(f"Final Hash        : {seal[2]}")
        print(f"Total Logs        : {seal[3]}")
        print(f"Seal Timestamp    : {seal[4]}")
        print(f"Seal Version      : {seal[5]}")
        print(f"Algorithm         : {seal[6]}")
        print(f"Digital Signature : {str(seal[7])[:60]}...")
        print("-" * 70)


def get_latest_seal(index_name):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            index_name,
            final_hash,
            total_logs,
            seal_timestamp,
            seal_version,
            algorithm,
            digital_signature
        FROM seal_metadata
        WHERE index_name = ?
        ORDER BY id DESC
        LIMIT 1
    """, (index_name,))

    seal = cursor.fetchone()

    conn.close()

    return seal

def get_all_seals():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, index_name, final_hash, total_logs,
               seal_timestamp, seal_version, algorithm, digital_signature
        FROM seal_metadata
        ORDER BY id DESC
    """)

    seals = cursor.fetchall()
    conn.close()

    return seals
