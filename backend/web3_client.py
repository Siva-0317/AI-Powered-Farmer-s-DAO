# backend/web3_client.py
import os, json, time
from dotenv import load_dotenv
from web3 import Web3, exceptions
from web3.middleware import geth_poa_middleware

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv()

SEPOLIA_RPC = os.getenv("SEPOLIA_RPC")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
WALLET_ADDRESS = os.getenv("WALLET_ADDRESS")
INSURANCE_POOL = os.getenv("INSURANCE_POOL")
STABLE_TOKEN = os.getenv("STABLE_TOKEN")

# Correct ABI paths
POOL_ABI_PATH = os.path.join(BASE_DIR, "abi", "FarmInsurancePool.json")
TOKEN_ABI_PATH = os.path.join(BASE_DIR, "abi", "TestStableToken.json")

if not SEPOLIA_RPC:
    raise RuntimeError("SEPOLIA_RPC must be set")

w3 = Web3(Web3.HTTPProvider(SEPOLIA_RPC))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

if not w3.is_connected():
    raise RuntimeError("Web3 provider not connected - check SEPOLIA_RPC")


def load_abi(path):
    abs_path = os.path.abspath(path)
    if not os.path.exists(abs_path):
        raise FileNotFoundError(f"ABI file not found: {abs_path}")
    with open(abs_path, "r", encoding="utf-8") as f:
        j = json.load(f)
        return j.get("abi", j)


# Load ABIs if addresses are set
pool_abi = load_abi(POOL_ABI_PATH) if INSURANCE_POOL else None
stable_abi = load_abi(TOKEN_ABI_PATH) if STABLE_TOKEN else None

# Initialize contracts
pool_contract = (
    w3.eth.contract(address=Web3.to_checksum_address(INSURANCE_POOL), abi=pool_abi)
    if INSURANCE_POOL and pool_abi
    else None
)

stable_contract = (
    w3.eth.contract(address=Web3.to_checksum_address(STABLE_TOKEN), abi=stable_abi)
    if STABLE_TOKEN and stable_abi
    else None
)


def _build_and_send(tx_dict, wait_for_receipt=True, timeout=120):
    if not PRIVATE_KEY or not WALLET_ADDRESS:
        raise RuntimeError("PRIVATE_KEY and WALLET_ADDRESS must be set")

    tx_dict.setdefault(
        "nonce", w3.eth.get_transaction_count(Web3.to_checksum_address(WALLET_ADDRESS))
    )
    if "gasPrice" not in tx_dict:
        tx_dict["gasPrice"] = w3.to_wei("20", "gwei")
    if "gas" not in tx_dict:
        tx_dict["gas"] = 300_000

    signed = w3.eth.account.sign_transaction(tx_dict, private_key=PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
    tx_hex = w3.to_hex(tx_hash)
    result = {"tx_hash": tx_hex}

    if wait_for_receipt:
        try:
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=timeout)
            result["receipt"] = dict(receipt)
            result["status"] = receipt.status
        except exceptions.TimeExhausted:
            result["status"] = "pending"
    return result


def submit_claim_to_chain(
    policy_id: int, stress_level: int, payout_percentage_scaled: int, wait_for_receipt=True
):
    if pool_contract is None:
        raise RuntimeError("Pool contract not initialized. Check INSURANCE_POOL and ABI")
    try:
        fn = pool_contract.functions.submitOracleData(
            policy_id, int(stress_level), int(payout_percentage_scaled)
        )
        tx = fn.build_transaction({"from": Web3.to_checksum_address(WALLET_ADDRESS)})
        return _build_and_send(tx, wait_for_receipt=wait_for_receipt)
    except Exception as e:
        return {"error": str(e)}


def execute_payout_onchain(policy_id: int, wait_for_receipt=True):
    if pool_contract is None:
        raise RuntimeError("Pool contract not initialized")
    try:
        fn = pool_contract.functions.executePayout(policy_id)
        tx = fn.build_transaction({"from": Web3.to_checksum_address(WALLET_ADDRESS)})
        return _build_and_send(tx, wait_for_receipt=wait_for_receipt)
    except Exception as e:
        return {"error": str(e)}


def authorize_oracle(oracle_addr: str):
    if pool_contract is None:
        raise RuntimeError("Pool contract not initialized")
    try:
        fn = pool_contract.functions.authorizeOracle(Web3.to_checksum_address(oracle_addr))
        tx = fn.build_transaction({"from": Web3.to_checksum_address(WALLET_ADDRESS)})
        return _build_and_send(tx)
    except Exception as e:
        return {"error": str(e)}


def get_tx_status(tx_hash: str):
    try:
        receipt = w3.eth.get_transaction_receipt(tx_hash)
        return {"tx_hash": tx_hash, "status": receipt.status, "receipt": dict(receipt)}
    except Exception as e:
        return {"error": str(e)}
