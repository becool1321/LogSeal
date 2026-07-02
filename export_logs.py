import json
import os
from datetime import datetime, UTC
from opensearchpy import OpenSearch

OPENSEARCH_URL = os.getenv("OPENSEARCH_URL", "http://opensearch:9200")

es = OpenSearch(
    hosts=[OPENSEARCH_URL],
    use_ssl=False,
    verify_certs=False
)


def export_logs(index_name=None):
    if index_name is None:
        index_name = "logs-" + datetime.now(UTC).strftime("%Y-%m-%d")

    os.makedirs("crypto/archive", exist_ok=True)
    output_file = f"crypto/archive/{index_name}.json"

    response = es.search(
        index=index_name,
        body={
            "size": 1000,
            "sort": [{"timestamp": {"order": "asc"}}],
            "query": {"match_all": {}}
        }
    )

    logs = [hit["_source"] for hit in response["hits"]["hits"]]

    with open(output_file, "w") as f:
        json.dump(logs, f, indent=4)

    print(f"[EXPORT COMPLETE] {output_file}")
    return output_file


if __name__ == "__main__":
    export_logs()
