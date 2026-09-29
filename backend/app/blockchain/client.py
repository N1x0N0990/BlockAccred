"""Talks to the local Hardhat blockchain using web3.py."""
import json
import os
from pathlib import Path
from dotenv import load_dotenv
from web3 import Web3
from web3.exceptions import ContractLogicError

load_dotenv()
RPC_URL = os.getenv("BLOCKCHAIN_RPC_URL", "http://127.0.0.1:8545")
DEPLOYMENT_FILE = os.getenv("DEPLOYMENT_FILE", "../blockchain/deployment.json")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")
PRIVATE_KEY = os.getenv("BLOCKCHAIN_PRIVATE_KEY")

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DEPLOYMENT_FILE = str((BASE_DIR / DEPLOYMENT_FILE).resolve()) if not os.path.isabs(DEPLOYMENT_FILE) else DEPLOYMENT_FILE

FIELDS = ["evidenceId", "documentHash", "institutionId", "timestamp", "submitter", "version", "status"]


class ChainUnavailable(Exception):
    """Raised when the Hardhat node is not running or the contract is not deployed."""


def _connect():
    if CONTRACT_ADDRESS:
        address = CONTRACT_ADDRESS
        if os.path.exists(DEPLOYMENT_FILE):
            with open(DEPLOYMENT_FILE) as f:
                dep = json.load(f)
            abi = dep.get("abi")
        else:
            with open(Path(__file__).with_name("contract_abi.json")) as f:
                abi = json.load(f)
    else:
        if not os.path.exists(DEPLOYMENT_FILE):
            raise ChainUnavailable("Contract not deployed yet. Run 'npm run deploy' inside the blockchain folder.")
        with open(DEPLOYMENT_FILE) as f:
            dep = json.load(f)
        address = dep["address"]
        abi = dep["abi"]

    w3 = Web3(Web3.HTTPProvider(RPC_URL, request_kwargs={"timeout": 10}))
    try:
        if not w3.is_connected():
            raise ChainUnavailable("Blockchain node is not running or RPC URL is invalid.")
        code = w3.eth.get_code(Web3.to_checksum_address(address))
    except ChainUnavailable:
        raise
    except Exception:
        raise ChainUnavailable("Blockchain node is not running or RPC URL is invalid.")
    if not code or len(code) == 0:
        raise ChainUnavailable("Contract not found on this network. Deploy the contract or set the correct CONTRACT_ADDRESS.")
    contract = w3.eth.contract(address=Web3.to_checksum_address(address), abi=abi)
    return w3, contract, address


def _send_transaction(w3, contract_function):
    if PRIVATE_KEY:
        account = w3.eth.account.from_key(PRIVATE_KEY)
        transaction = contract_function.build_transaction({
            "from": account.address,
            "nonce": w3.eth.get_transaction_count(account.address),
            "chainId": w3.eth.chain_id,
        })
        signed = w3.eth.account.sign_transaction(transaction, PRIVATE_KEY)
        raw_transaction = getattr(signed, "raw_transaction", None) or signed.rawTransaction
        tx_hash = w3.eth.send_raw_transaction(raw_transaction)
    else:
        tx_hash = contract_function.transact({"from": w3.eth.accounts[0]})
    return w3.eth.wait_for_transaction_receipt(tx_hash), tx_hash


def status():
    try:
        w3, contract, address = _connect()
        return {"online": True, "address": address, "chain_id": w3.eth.chain_id,
                "block_number": w3.eth.block_number, "total_records": contract.functions.totalRecords().call(),
                "network": os.getenv("BLOCKCHAIN_NETWORK", "Blockchain")}
    except ChainUnavailable as e:
        return {"online": False, "message": str(e)}


def register_evidence(code: str, version: int, doc_hash: str, institution_code: str):
    w3, contract, address = _connect()
    receipt, tx = _send_transaction(
        w3, contract.functions.registerEvidence(code, version, doc_hash, institution_code)
    )
    return {"tx_hash": tx.hex() if hasattr(tx, "hex") else str(tx), "block_number": receipt.blockNumber, "contract_address": address}


def get_evidence(code: str, version: int):
    """Returns the on-chain record as a dict, or None if it does not exist."""
    w3, contract, _ = _connect()
    try:
        res = contract.functions.getEvidence(code, version).call()
    except ContractLogicError:
        return None
    rec = dict(zip(FIELDS, res))
    rec["timestamp"] = int(rec["timestamp"])
    rec["version"] = int(rec["version"])
    return rec


def verify_evidence(code: str, version: int, status_text: str):
    w3, contract, _ = _connect()
    _, tx = _send_transaction(w3, contract.functions.verifyEvidence(code, version, status_text))
    return tx.hex() if hasattr(tx, "hex") else str(tx)
