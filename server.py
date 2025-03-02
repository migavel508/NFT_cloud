import os
import json
import time
import requests
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template
from web3 import Web3
from eth_account import Account
from requests.exceptions import RequestException

# Load environment variables
load_dotenv()

# Constants
PINATA_JWT = os.getenv("PINATA_JWT")
INFURA_PROJECT_ID = os.getenv("INFURA_PROJECT_ID")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
SENDER_ADDRESS = os.getenv("SENDER_ADDRESS")

# Verify private key matches sender address
derived_address = Account.from_key(PRIVATE_KEY).address
if derived_address.lower() != SENDER_ADDRESS.lower():
    raise ValueError("❌ PRIVATE_KEY does not match SENDER_ADDRESS!")

# Setup Web3
infura_url = f"https://sepolia.infura.io/v3/{INFURA_PROJECT_ID}"
w3 = Web3(Web3.HTTPProvider(infura_url))
if not w3.is_connected():
    raise ConnectionError("❌ Failed to connect to Infura.")
print("✅ Connected to Infura!")

# Flask Setup
app = Flask(__name__)

# Create "uploads" folder if it doesn't exist
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Store Minted NFTs
minted_nfts = []

# 📌 **Pinata Upload Function**
def upload_to_pinata(file_path):
    if not os.path.exists(file_path):
        return {"error": f"File '{file_path}' not found!"}

    url = "https://api.pinata.cloud/pinning/pinFileToIPFS"
    headers = {"Authorization": f"Bearer {PINATA_JWT}"}

    try:
        with open(file_path, "rb") as file:
            files = {"file": file}
            response = requests.post(url, files=files, headers=headers, timeout=30)
            response.raise_for_status()
            ipfs_hash = response.json().get("IpfsHash")
            return {"success": True, "ipfs_hash": ipfs_hash}
    except RequestException as e:
        return {"error": f"Failed to upload to Pinata: {str(e)}"}

# 📌 **Wait for Pending Transactions to Clear**
def wait_for_nonce_sync():
    while True:
        pending_nonce = w3.eth.get_transaction_count(SENDER_ADDRESS, "pending")
        latest_nonce = w3.eth.get_transaction_count(SENDER_ADDRESS, "latest")
        if pending_nonce == latest_nonce:
            break
        print("⏳ Waiting for pending transactions to clear...")
        time.sleep(5)  # Wait for 5 seconds before checking again

# 📌 **Mint NFT Function**
def mint_nft(ipfs_hash):
    try:
        wait_for_nonce_sync()  # Ensure nonce is synced before minting
        
        abi = json.load(open("contract_abi.json"))  
        contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=abi)

        nonce = w3.eth.get_transaction_count(SENDER_ADDRESS, "pending")  
        base_gas_price = w3.eth.gas_price
        adjusted_gas_price = int(base_gas_price * 1.2)  # Increase by 20%

        txn = contract.functions.safeMint(SENDER_ADDRESS, f"ipfs://{ipfs_hash}").build_transaction({
            "chainId": 11155111,
            "gas": 500000,
            "gasPrice": adjusted_gas_price,
            "nonce": nonce,
        })

        signed_txn = w3.eth.account.sign_transaction(txn, private_key=PRIVATE_KEY)
        txn_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction).hex()

        # Store minted NFT details
        minted_nfts.append({"transaction_hash": txn_hash, "ipfs_hash": ipfs_hash})

        return {"success": True, "transaction_hash": txn_hash}
    except Exception as e:
        return {"error": str(e)}

# 📌 **Upload API Route**
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided!"}), 400

    file = request.files['file']
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(file_path)

    result = upload_to_pinata(file_path)
    return jsonify(result)

# 📌 **Mint API Route**
@app.route('/mint', methods=['POST'])
def mint():
    data = request.json
    ipfs_hash = data.get("ipfs_hash")
    if not ipfs_hash:
        return jsonify({"error": "Missing IPFS hash"}), 400

    result = mint_nft(ipfs_hash)
    return jsonify(result)

# 📌 **Minting History API**
@app.route('/history')
def history():
    return render_template("history.html", minted_nfts=minted_nfts)

# 📌 **Serve Homepage**
@app.route('/')
def home():
    return render_template("index.html")

# 📌 **Run Flask Server**
if __name__ == '__main__':
    app.run(debug=True, port=5003)
