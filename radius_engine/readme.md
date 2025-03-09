# Radius Engine

A Python module for interacting with the Radius Network, enabling Web3 transactions and smart contract interactions. This engine provides a simple interface for checking network connection, getting wallet balances, and executing transactions on the Radius Network.

## Features

- Connect to Radius Network using RPC endpoints
- Check network connection status and block number
- Get wallet balances
- Send transactions between addresses
- Process deal details from JSON files

## Setup

1. Install required packages:
```bash
pip install -r requirements.txt
```

2. Set up environment variables in `.env` file (use `.env_template` as a guide) and add your environment variables.
```bash
cp .env_template .env
```

## Run a few mock examples:

For a successful run, provide a path to a JSON file containing deal details.
```bash
python radius_engine/example.py --input_file agents/outputs/example_success.json
```

For a run that fails, provide a path to a JSON file containing deal details.
```bash
python radius_engine/example.py --input_file agents/outputs/example_no_deal.json
```
