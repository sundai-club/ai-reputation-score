import os
from groq import Groq
import json

def score(conversation = ""):
    
    with open('message.txt', 'r') as file:
        conversation = str(json.load(file)['messages'])

    client = Groq(
        api_key="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",
    )

    prompt = "You are a Scoring Agent assessing the conversation of two Agents based on the following formula: \n score=(0.3*Relevance)+(0.25*Accuracy)+(0.15*Sentiment)+(0.1*Compliance)+(0.2*Resolution) \n Based on the formula only give me the numeric score between 1 to 5 for both agents. For eg. Agent1: 5, Agent2: 4.4; Agent1: 4.7, Agent2: 3.8\n"
    
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt + conversation,
            }
        ],
        model="llama-3.3-70b-versatile",
    )

    score_string = chat_completion.choices[0].message.content
    parts = score_string.split(", ")

    # Extract Agent1 score
    agent1_label, agent1_score = parts[0].split(": ")
    agent1_score = float(agent1_score)  # Convert to float

    # Extract Agent2 score
    agent2_label, agent2_score = parts[1].split(": ")
    agent2_score = float(agent2_score)  # Convert to float

    return agent1_score, agent2_score

# print(score())