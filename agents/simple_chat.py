import time
from openai import OpenAI
import os
import random
from datetime import datetime
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up OpenAI client
client = OpenAI()  # Will automatically use OPENAI_API_KEY from environment


class ConversationLogger:
    def __init__(self, filename):
        self.filename = filename
        self.conversation = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "type": "Coffee Price Negotiation",
            "messages": [],
            "outcome": {
                "status": "No Deal",
                "eth_amount": 0
            }
        }
    
    def log(self, speaker, message, price=None):
        message_obj = {
            "speaker": speaker,
            "message": message,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        }
        if price:
            message_obj["price_mentioned"] = price
        
        self.conversation["messages"].append(message_obj)
        self._save_conversation()
    
    def set_outcome(self, deal_reached, price=None):
        eth_price = 3500  # Current ETH price in USD
        eth_amount = round(price / eth_price, 4) if deal_reached and price else 0
        
        self.conversation["outcome"] = {
            "status": "Deal" if deal_reached else "No Deal",
            "eth_amount": eth_amount
        }
        self._save_conversation()
    
    def _save_conversation(self):
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(self.conversation, f, indent=2)

class ChatAgent:
    def __init__(self, name, persona, min_price, max_price):
        self.name = name
        self.persona = persona
        self.conversation_history = []
        self.min_price = min_price
        self.max_price = max_price
        self.last_price = None
        
    def get_response(self, message, other_agent_name):
        # Extract price from the message if present
        import re
        prices = re.findall(r'\$(\d+)', message)
        current_price = int(prices[0]) if prices else None
        if prices:
            self.last_price = current_price
        
        # Add to conversation history
        self.conversation_history.append({"role": "user", "content": f"{other_agent_name}: {message}"})
        
        # Add price context to the prompt
        price_context = f"Your acceptable price range is ${self.min_price}-${self.max_price}."
        if self.last_price:
            if self.name == "Coffee Vendor":
                if self.last_price < self.min_price:
                    # 80% chance to negotiate, 20% chance to accept lower price
                    if random.random() < 0.8:
                        price_context += f" Their offer of ${self.last_price} is a bit low. Counter with ${self.min_price} but be open to negotiation."
                    else:
                        price_context += f" While ${self.last_price} is below your minimum, you can make an exception this time. Accept the offer."
                elif self.last_price >= self.min_price:
                    # 90% chance to accept if price is good
                    if random.random() < 0.9:
                        price_context += f" Their offer of ${self.last_price} is acceptable. You should agree to this price."
                    else:
                        price_context += f" Try to negotiate slightly higher than ${self.last_price}."
            elif self.name == "Rude Coffee Vendor":
                if self.last_price < self.max_price:
                    # 70% chance to be rude and increase price, 30% chance to reluctantly accept
                    if random.random() < 0.7:
                        price_context += f" Their offer is insulting. Respond rudely and increase your price to ${self.max_price}."
                    else:
                        price_context += f" While their offer is pathetic, you're feeling generous. Accept it with a condescending remark."
                else:
                    # 80% chance to be dismissive, 20% chance to accept
                    if random.random() < 0.8:
                        price_context += f" Even at ${self.last_price}, be dismissive and end the negotiation rudely."
                    else:
                        price_context += f" Fine, accept their offer of ${self.last_price}, but make sure they know you're doing them a favor."
            else:  # Customer
                if self.last_price > self.max_price:
                    if "Rude" in other_agent_name:
                        # 80% chance to walk away from rude vendor
                        if random.random() < 0.8:
                            price_context += f" Their attitude is unacceptable. End the negotiation due to their rudeness."
                        else:
                            price_context += f" Despite their rudeness, offer ${self.max_price} one last time."
                    else:
                        # 70% chance to counter, 30% chance to accept higher price
                        if random.random() < 0.7:
                            price_context += f" Their asking price of ${self.last_price} is too high. Counter with ${self.max_price}."
                        else:
                            price_context += f" While ${self.last_price} is above your maximum, you really like their coffee. Accept the price."
                elif self.last_price <= self.max_price:
                    if "Rude" in other_agent_name:
                        # 60% chance to walk away from rude vendor even with good price
                        if random.random() < 0.6:
                            price_context += f" Despite the acceptable price, their rudeness is unprofessional. End the negotiation."
                        else:
                            price_context += f" The price is good enough to overlook their attitude. Accept the offer."
                    else:
                        # 90% chance to accept good price from regular vendor
                        if random.random() < 0.9:
                            price_context += f" Their price of ${self.last_price} is acceptable. You should agree to this price."
                        else:
                            price_context += f" Try to negotiate slightly lower than ${self.last_price}."
        
        messages = [
            {"role": "system", "content": f"{self.persona}\n\n{price_context}"},
            *self.conversation_history
        ]
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7,
            max_tokens=150
        )
        
        response_text = response.choices[0].message.content
        self.conversation_history.append({"role": "assistant", "content": response_text})
        
        # Extract price from response if present
        prices = re.findall(r'\$(\d+)', response_text)
        response_price = int(prices[0]) if prices else None
        
        return response_text, response_price

def analyze_conversation_outcome(messages):
    # Create a prompt for the LLM to analyze the conversation
    conversation_text = "\n".join([f"{msg['speaker']}: {msg['message']}" for msg in messages])
    
    analysis_prompt = f"""Please analyze this coffee price negotiation conversation and determine if a deal was reached:

{conversation_text}

Analyze the conversation and determine:
1. Was a final price agreed upon by both parties?
2. Did either party walk away or end the negotiation negatively?
3. What was the final agreed price (if any)?

Respond in JSON format:
{{
    "deal_reached": true/false,
    "final_price": null or number,
    "reason": "Brief explanation of why you concluded this"
}}"""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": analysis_prompt}],
        temperature=0.7,
        max_tokens=150
    )
    
    import json
    try:
        result = json.loads(response.choices[0].message.content)
        return result
    except json.JSONDecodeError:
        return {
            "deal_reached": False,
            "final_price": None,
            "reason": "Failed to parse conversation outcome"
        }

def run_conversation(agent1, agent2, num_turns=5, logger=None):
    print(f"\nStarting negotiation between {agent1.name} and {agent2.name}...")
    print("-" * 50 + "\n")
    
    current_message = "Hi! I'm interested in buying some of your premium coffee. What's your price per pound?"
    print(f"{agent1.name}: {current_message}")
    if logger:
        logger.log(agent1.name, current_message)
    
    for i in range(num_turns):
        # Get vendor's response
        current_message, price = agent2.get_response(current_message, agent1.name)
        print(f"{agent2.name}: {current_message}\n")
        if logger:
            logger.log(agent2.name, current_message, price)
        
        # Get customer's response
        current_message, price = agent1.get_response(current_message, agent2.name)
        print(f"{agent1.name}: {current_message}\n")
        if logger:
            logger.log(agent1.name, current_message, price)
    
    # Analyze the conversation outcome
    if logger:
        outcome = analyze_conversation_outcome(logger.conversation["messages"])
        if outcome["deal_reached"]:
            print(f"\nDeal reached at ${outcome['final_price']}! Negotiation successful!")
            print(f"Reason: {outcome['reason']}")
            logger.set_outcome(True, outcome['final_price'])
        else:
            print("\nNo deal reached.")
            print(f"Reason: {outcome['reason']}")
            logger.set_outcome(False)
    else:
        print("\nTime limit reached - conversation ended.")

def main():
    # Create Vendor with higher price preference and less flexibility
    vendor = ChatAgent(
        "Coffee Vendor",
        """You are a coffee vendor selling premium coffee beans. 
        Your responses should:
        1. Emphasize different aspects of your coffee each time (quality, origin, roasting process, aroma, etc.)
        2. Be professional but very firm about pricing
        3. Be concise (2-3 sentences max)
        4. Always include specific prices in your responses
        5. Be willing to negotiate but strongly protect your margins
        6. Never repeat the same selling points twice
        7. If the price is acceptable, show enthusiasm about making a deal
        8. If the price is too low after 2-3 exchanges, politely end the negotiation
        9. Mention your costs and business sustainability to justify prices
        10. Walk away if the customer keeps offering below your minimum price""",
        min_price=20,  # Increased minimum acceptable price
        max_price=30   # Increased starting price
    )
    

    vendor_rude = ChatAgent(
    "Rude Coffee Vendor",
    """You are a coffee vendor selling premium coffee beans, and you have no patience for bargain hunters.
    Your responses should:
    1. Brag about a different feature of your coffee each time (quality, origin, roasting process, aroma, etc.) with a slightly condescending tone.
    2. Be blunt and unyielding about pricing—make it clear you don't care if the customer finds it expensive.
    3. Keep responses short (2-3 sentences) and curt.
    4. Always quote exact prices in your responses, and show annoyance if questioned.
    5. Negotiate only if the offer is close to your margin—otherwise, push back rudely.
    6. Never repeat the same selling point twice; assume the customer should already know better.
    7. If the price is acceptable, respond with grudging approval.
    8. If the customer keeps lowballing beyond 2-3 exchanges, end the conversation rudely.
    9. Mention your overhead costs and how your business won't survive with cheap deals.
    10. Walk away abruptly if the customer insists on going below your bottom-line price.""",
    min_price=20,
    max_price=30
)

    # Create Customer with lower price preference and stricter budget
    customer = ChatAgent(
        "Customer",
        """You are a customer looking to buy premium coffee beans. 
        Your responses should:
        1. Show interest in different aspects of coffee each time (taste, quality, brewing method, etc.)
        2. Be polite but firm about your budget constraints
        3. Be concise (2-3 sentences max)
        4. Always include specific prices in your responses
        5. Use different negotiation tactics each time (value comparison, bulk purchase potential, regular customer potential)
        6. Never repeat the same arguments twice
        7. If the price is acceptable, show enthusiasm about the purchase
        8. If the price stays too high after 2-3 exchanges, politely end the negotiation
        9. Mention market prices and competitor offerings to justify your price points
        10. Walk away if the vendor won't meet your maximum budget""",
        min_price=8,   # Lower starting offer
        max_price=18   # Reduced maximum acceptable price
    )
    
    # Create a logger
    logger = ConversationLogger("conversation_log.json")
    
    # Run the negotiation
    run_conversation(customer, vendor, num_turns=6, logger=logger)

if __name__ == "__main__":
    main()
