# Monitoring Radius Agents to Improve Ethetium Transactions Trustworthiness

This project involves developing a system for monitoring Radius Agents to improve Ethetium transactions trustworthiness. The system will analyze the behavior of Radius Agents on the Ethetium network and provide insights into the trustworthiness of these agents. This information can be used to optimize the performance of Ethetium transactions, as well as improve customer experience.

## Installation

1. Clone the repository
```bash
git clone https://github.com/vprudente/ai-reputation-score
```

2. Install the requirements
```bash
cd ai-reputation-score
pip install -r requirements.txt
```

3. Define the environment variables. Make sure to add your API keys and the agents' eth addresses to the `.env` file.
```bash
cp .env_template .env
```

## Usage

1. Run the agents
```bash
python agents/simple_chat.py
```

2. Execute the radius engine to process deal details based on the agents interaction
```bash
python radius_engine/radius_engine.py --input_file agents/conversation_log.json
```

