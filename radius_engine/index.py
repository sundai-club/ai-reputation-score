import json
from dotenv import load_dotenv
import os
from web3 import Web3

load_dotenv()

RADIUS_RPC_ENDPOINT_ID = os.getenv("RADIUS_RPC_ENDPOINT_ID")
PRIVATE_KEY_AGENT1 = os.getenv("PRIVATE_KEY_AGENT1")  # Your wallet's private key
FROM_ADDRESS_AGENT1 = os.getenv("FROM_ADDRESS_AGENT1")  # Your wallet address
PRIVATE_KEY_AGENT2 = os.getenv("PRIVATE_KEY_AGENT2")  # Your wallet's private key
TO_ADDRESS_AGENT2 = os.getenv("TO_ADDRESS_AGENT2")  # Your wallet address

# Initialize Web3
rpc_url = f"https://rpc.testnet.tryradi.us/{RADIUS_RPC_ENDPOINT_ID}"
w3 = Web3(Web3.HTTPProvider(rpc_url))

def check_connection():
    """Check if we're connected to the network"""
    if w3.is_connected():
        print(f"Connected to Radius Network")
        print(f"Current block number: {w3.eth.block_number}")
    else:
        print("Failed to connect to Radius Network")

def get_balance(address):
    """Get balance of an address"""
    balance = w3.eth.get_balance(address)
    balance_eth = w3.from_wei(balance, 'ether')
    return balance_eth

def send_transaction(from_address, from_private_key, to_address, amount_in_ether):
    """Send a transaction on the Radius network"""
    try:
        # Convert ether to wei
        amount_in_wei = w3.to_wei(amount_in_ether, 'ether')
        
        # Prepare transaction
        nonce = w3.eth.get_transaction_count(from_address)
        transaction = {
            'nonce': nonce,
            'to': to_address,
            'value': amount_in_wei,
            'gas': 21000,  # Standard gas limit for ETH transfers
            'gasPrice': w3.eth.gas_price,
            'chainId': w3.eth.chain_id
        }
        
        # Sign transaction
        signed_txn = w3.eth.account.sign_transaction(transaction, from_private_key)
        
        # Send transaction
        tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
        # Wait for transaction receipt
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        
        print(f"Transaction successful!")
        print(f"Transaction hash: {tx_receipt.transactionHash.hex()}")
        return tx_receipt
        
    except Exception as e:
        print(f"Error sending transaction: {str(e)}")
        return None

if __name__ == "__main__":
    # Check connection
    check_connection()
    
    # Example: Get balance
    if FROM_ADDRESS_AGENT1:
        balance = get_balance(FROM_ADDRESS_AGENT1)
        print(f"Balance of {FROM_ADDRESS_AGENT1}: {balance} ETH")
    
    # Example: To send a transaction
    to_address = TO_ADDRESS_AGENT2
    amount = 0.0001  # Amount in ETH
    print("BEFORE TRANSACTION")
    print(f"Sending {amount} ETH to {to_address}")
    print(f"From address: {FROM_ADDRESS_AGENT1}")
    print(f"Current balance: {get_balance(FROM_ADDRESS_AGENT1)} ETH")
    print(f"To address: {to_address}")
    print(f"Current balance: {get_balance(to_address)} ETH")
    transaction_receipt = send_transaction(FROM_ADDRESS_AGENT1, PRIVATE_KEY_AGENT1, to_address, amount)
    print("AFTER TRANSACTION")
    print(f"Balance of {FROM_ADDRESS_AGENT1}: {get_balance(FROM_ADDRESS_AGENT1)} ETH")
    print(f"Balance of {to_address}: {get_balance(to_address)} ETH")
    print(f"Transaction receipt: {transaction_receipt}")




###################################################################
# url = f"https://rpc.testnet.tryradi.us/{RADIUS_RPC_ENDPOINT_ID}"

# payload = {
#     "jsonrpc": "2.0",
#     "method": "eth_blockNumber",
#     "params": [],
#     "id": 1
# }

# headers = {'content-type': 'application/json'}

# response = requests.post(url, data=json.dumps(payload), headers=headers).json()

# print(response)