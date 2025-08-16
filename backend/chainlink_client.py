import os, json, requests

CHAINLINK_WEBHOOK_URL = os.environ.get("CHAINLINK_WEBHOOK_URL", "")
CHAINLINK_API_KEY = os.environ.get("CHAINLINK_API_KEY", "")
PUSH_TO_CHAINLINK = os.environ.get("PUSH_TO_CHAINLINK", "false").lower() == "true"

def push_prediction_to_chainlink(payload: dict) -> dict:
    """
    Push mode: POST the result to a Chainlink Node job (webhook job) if you want the node to ingest it.
    If you're using Chainlink Functions (pull mode), keep PUSH_TO_CHAINLINK=false
    and let the DON call your /oracle/predict endpoint instead.
    """
    if not PUSH_TO_CHAINLINK:
        return {"skipped": True, "reason": "PUSH_TO_CHAINLINK=false"}
    if not CHAINLINK_WEBHOOK_URL:
        return {"skipped": True, "reason": "missing CHAINLINK_WEBHOOK_URL"}

    headers = {"Content-Type": "application/json"}
    if CHAINLINK_API_KEY:
        headers["X-API-Key"] = CHAINLINK_API_KEY

    try:
        r = requests.post(CHAINLINK_WEBHOOK_URL, headers=headers, data=json.dumps(payload), timeout=20)
        return {"status_code": r.status_code, "text": r.text}
    except Exception as e:
        return {"error": str(e)}
