from opensearchpy.exceptions import NotFoundError

from crypto.index_sealer import generate_hash_chain
from crypto.seal_metadata import get_latest_seal
from crypto.signer import verify_signature
from alerts.alert_manager import create_alert
from security.replay_protection import check_replay


def verify_index(index_name):
    seal = get_latest_seal(index_name)

    if not seal:
        print(f"[ERROR] No seal found for {index_name}")
        return {
            "status": False,
            "index_name": index_name,
            "message": "No seal metadata found for this index.",
            "stored_hash": None,
            "current_hash": None,
            "total_logs": 0,
            "signature_valid": False
        }

    stored_hash = seal[2]
    stored_signature = seal[7]
    stored_version = seal[5]

    replay_valid, latest_version = check_replay(
        index_name,
        stored_version
    )

    if not replay_valid:
        print("\n[REPLAY ATTACK DETECTED]")
        print(f"Stored Seal Version : {stored_version}")
        print(f"Latest Seal Version : {latest_version}")

        create_alert(
            "REPLAY_ATTACK",
            index_name,
            f"Old seal version {stored_version} reused. Latest known version is {latest_version}.",
            "CRITICAL"
        )

        return {
            "status": False,
            "index_name": index_name,
            "message": "Replay attack detected. Old seal metadata was reused.",
            "stored_hash": stored_hash,
            "current_hash": None,
            "total_logs": 0,
            "signature_valid": False
        }

    try:
        current_hash, total_logs = generate_hash_chain(index_name)

    except NotFoundError:
        print(f"[ERROR] OpenSearch index not found: {index_name}")

        create_alert(
            "INDEX_NOT_FOUND",
            index_name,
            f"Verification failed because index {index_name} was not found.",
            "HIGH"
        )

        return {
            "status": False,
            "index_name": index_name,
            "message": "OpenSearch index not found.",
            "stored_hash": stored_hash,
            "current_hash": None,
            "total_logs": 0,
            "signature_valid": False
        }

    except Exception as e:
        print(f"[ERROR] Verification failed: {e}")

        return {
            "status": False,
            "index_name": index_name,
            "message": f"Verification error: {e}",
            "stored_hash": stored_hash,
            "current_hash": None,
            "total_logs": 0,
            "signature_valid": False
        }

    print("\n[VERIFY RESULT]")
    print(f"Index Name  : {index_name}")
    print(f"Stored Hash : {stored_hash}")
    print(f"Current Hash: {current_hash}")
    print(f"Total Logs  : {total_logs}")

    if stored_hash != current_hash:
        print("\n[TAMPER DETECTED] Hash mismatch found.")

        create_alert(
            "HASH_MISMATCH",
            index_name,
            "Stored hash does not match recalculated hash. Possible log tampering detected.",
            "CRITICAL"
        )

        return {
            "status": False,
            "index_name": index_name,
            "message": "Hash mismatch found. Possible log tampering detected.",
            "stored_hash": stored_hash,
            "current_hash": current_hash,
            "total_logs": total_logs,
            "signature_valid": False
        }

    if not stored_signature:
        print("\n[TAMPER DETECTED] Missing digital signature.")

        create_alert(
            "MISSING_SIGNATURE",
            index_name,
            "Seal metadata does not contain a digital signature.",
            "HIGH"
        )

        return {
            "status": False,
            "index_name": index_name,
            "message": "Missing digital signature in seal metadata.",
            "stored_hash": stored_hash,
            "current_hash": current_hash,
            "total_logs": total_logs,
            "signature_valid": False
        }

    signature_valid = verify_signature(current_hash, stored_signature)

    if not signature_valid:
        print("\n[TAMPER DETECTED] Digital signature is invalid.")

        create_alert(
            "INVALID_SIGNATURE",
            index_name,
            "RSA digital signature verification failed. Seal may be forged or modified.",
            "CRITICAL"
        )

        return {
            "status": False,
            "index_name": index_name,
            "message": "Digital signature is invalid.",
            "stored_hash": stored_hash,
            "current_hash": current_hash,
            "total_logs": total_logs,
            "signature_valid": False
        }

    print("\n[INDEX VERIFIED] Hash matched and RSA signature is valid.")

    return {
        "status": True,
        "index_name": index_name,
        "message": "Index verified successfully. Hash and RSA signature are valid.",
        "stored_hash": stored_hash,
        "current_hash": current_hash,
        "total_logs": total_logs,
        "signature_valid": True
    }
