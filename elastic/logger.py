import os
from datetime import datetime, UTC
from opensearchpy import OpenSearch

OPENSEARCH_URL = os.getenv(
    "OPENSEARCH_URL",
    "http://opensearch:9200"
)

es = OpenSearch(
    hosts=[OPENSEARCH_URL],
    use_ssl=False,
    verify_certs=False
)

def get_daily_index():
    return "logs-" + datetime.now(UTC).strftime("%Y-%m-%d")

def send_log(user_id, username, event_type, message, status="success"):

    index_name = get_daily_index()

    document = {
        "timestamp": datetime.now(UTC).isoformat(),
        "user_id": user_id,
        "username": username,
        "event_type": event_type,
        "message": message,
        "status": status,
        "source": "flask_web_app"
    }

    try:
        response = es.index(
            index=index_name,
            body=document,
            refresh=True
        )

        print(f"[OPENSEARCH] {event_type} stored in {index_name}")
        return response

    except Exception as e:
        print(f"[OPENSEARCH ERROR] {e}")
