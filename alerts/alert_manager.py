import os
from datetime import datetime, UTC
from opensearchpy import OpenSearch

OPENSEARCH_URL = os.getenv("OPENSEARCH_URL", "http://opensearch:9200")

es = OpenSearch(
    hosts=[OPENSEARCH_URL],
    use_ssl=False,
    verify_certs=False
)


def create_alert(alert_type, index_name, description, severity="HIGH"):
    document = {
        "timestamp": datetime.now(UTC).isoformat(),
        "alert_type": alert_type,
        "index_name": index_name,
        "description": description,
        "severity": severity,
        "source": "logseal_crypto_engine"
    }

    es.index(index="logseal-alerts", body=document, refresh=True)
    print("[ALERT CREATED]")


def get_recent_alerts():
    try:
        response = es.search(
            index="logseal-alerts",
            body={
                "size": 50,
                "sort": [{"timestamp": {"order": "desc"}}],
                "query": {"match_all": {}}
            }
        )

        return [hit["_source"] for hit in response["hits"]["hits"]]

    except Exception:
        return []
