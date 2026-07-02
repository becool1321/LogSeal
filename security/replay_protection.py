import json
import os
from datetime import datetime, UTC

REPLAY_STATE_FILE = "security/replay_state.json"


def load_state():
    if not os.path.exists(REPLAY_STATE_FILE):
        return {}

    with open(REPLAY_STATE_FILE, "r") as f:
        return json.load(f)


def save_state(state):
    os.makedirs("security", exist_ok=True)

    with open(REPLAY_STATE_FILE, "w") as f:
        json.dump(state, f, indent=4)


def update_latest_seal(index_name, seal_version):
    state = load_state()

    state[index_name] = {
        "latest_seal_version": seal_version,
        "updated_at": datetime.now(UTC).isoformat()
    }

    save_state(state)


def check_replay(index_name, seal_version):
    state = load_state()

    latest_version = state.get(index_name, {}).get("latest_seal_version", 0)

    if seal_version < latest_version:
        return False, latest_version

    return True, latest_version
