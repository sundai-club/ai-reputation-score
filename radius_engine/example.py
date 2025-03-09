from radius_engine import get_deal_details, send_transaction, get_balance
import os
import json
from dotenv import load_dotenv
from web3 import Web3
import argparse

load_dotenv()

RADIUS_RPC_ENDPOINT_ID = os.getenv("RADIUS_RPC_ENDPOINT_ID")
PRIVATE_KEY_AGENT1 = os.getenv("PRIVATE_KEY_AGENT1")  # Your wallet's private key
FROM_ADDRESS_AGENT1 = os.getenv("FROM_ADDRESS_AGENT1")  # Your wallet address
PRIVATE_KEY_AGENT2 = os.getenv("PRIVATE_KEY_AGENT2")  # Your wallet's private key
TO_ADDRESS_AGENT2 = os.getenv("TO_ADDRESS_AGENT2")  # Your wallet address

# Initialize Web3
rpc_url = f"https://rpc.testnet.tryradi.us/{RADIUS_RPC_ENDPOINT_ID}"
w3 = Web3(Web3.HTTPProvider(rpc_url))

# Create the addresses dict
addresses = {
    "Customer": FROM_ADDRESS_AGENT1,
    "Coffee Vendor": TO_ADDRESS_AGENT2
}
if __name__ == "__main__":
    # get json with deal details from user input params
    args = argparse.ArgumentParser()
    args.add_argument("--input_file", type=str, default="../agents/outputs/example_success.json", help="Input JSON file")
    args = args.parse_args()

    deal_details = get_deal_details(args.input_file)
    print(f"Agents agreed to have {deal_details['outcome']['status']} for the {deal_details['type']}.\n")
    if deal_details['outcome']['status'] == "Deal":
        print(f"It was agreed that {deal_details['outcome']['eth_amount']} ETH will be sent from {deal_details['messages'][0]['speaker']} to {deal_details['messages'][1]['speaker']}.")
        # Complete transaction
        from_address = addresses[deal_details['messages'][0]['speaker']]
        to_address = addresses[deal_details['messages'][1]['speaker']]
        amount = deal_details['outcome']['eth_amount']

        print(f"Sending {amount} ETH to {deal_details['messages'][1]['speaker']} - {to_address}")
        print(f"From address: {deal_details['messages'][0]['speaker']} - {from_address}")
        print(f"\nBEFORE TRANSACTION:")
        print(f"Current balance [{deal_details['messages'][0]['speaker']}]: {get_balance(from_address)} ETH")
        print(f"Current balance [{deal_details['messages'][1]['speaker']}]: {get_balance(to_address)} ETH")
        transaction_receipt = send_transaction(from_address, PRIVATE_KEY_AGENT1, to_address, amount)
        print(f"\nAFTER TRANSACTION:")
        print(f"Current balance [{deal_details['messages'][0]['speaker']}]: {get_balance(from_address)} ETH")
        print(f"Current balance [{deal_details['messages'][1]['speaker']}]: {get_balance(to_address)} ETH\n")
        print(f"Transaction receipt:\n{transaction_receipt}\n")
    else:
        print("Agents declined the deal.")