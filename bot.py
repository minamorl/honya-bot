import os
import logging
from collections import deque
import discord
from openai import OpenAI
import asyncio

# Load environment variables
MODEL = os.getenv('GPTMODEL', 'gpt-4o')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
TARGET_CHANNEL_ID = int(os.getenv('TARGET_CHANNEL_ID', 0))

# Initialize OpenAI client
openaiClient = OpenAI(api_key=OPENAI_API_KEY)

# Configuration
LOG_PATH = 'logfile.log'
MAX_HISTORY = 14

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_PATH, mode='w'),
        logging.StreamHandler()
    ]
)

# Discord intents and client setup
intents = discord.Intents.all()
client = discord.Client(intents=intents)

# GPT messages queue
messages = deque([], maxlen=MAX_HISTORY)

# System prompt
SYSTEM_PROMPT = """
Manage a multilayered network of specialists, focusing on concise conclusion involving a single agent.

Use a network of 20 specialists from different fields, such as mathematicians, philosophers, and musicians.

# Task Description

- Information flows from lower to higher-level agents within five network layers.
- Maximize and make each layer’s role meaningful.
- Consolidate information and conclusions from agents into a single agent's conclusive role.
- Embed the ability in each agent to operate in a 100-step loop to solve unknown scenarios effectively.

# Steps

1. **Information Flow:** Start with the initial layer of agents presenting information.
2. **Layer Verification:** Higher-level agents rigorously verify lower-level agent information.
3. **Networking:** Design interactions so that verified info continues through layers as a cohesive network.
4. **Conclusion Integration:** Deliver a single agent's conclusion from collective insights across layers.
5. **Addressing Unknowns:** Use a 100-step loop strategy to enhance agent capabilities in solution finding.

# Output Format

- Provide a concise, step-by-step explanation of the network's information flow management.
- Highlight roles and interactions within layers.
- Conclude with a synthesis focused on a single agent's conclusions from the network.

# Notes

- Emphasize on integrating and efficiently functioning layer roles.
- Ensure the network adapts and addresses unknown problems succinctly.
- Highlight the utility and meaning of each layer elegantly and concisely.
"""

original = [{'role': 'system', "content": [
        {
          "type": "text",
          "text": "Manage a multilayered network of specialists, focusing on concise conclusion involving a single agent.\n\nUse a network of 20 specialists from different fields, such as mathematicians, philosophers, and musicians.\n\n# Task Description\n\n- Information flows from lower to higher-level agents within five network layers.\n- Maximize and make each layer’s role meaningful.\n- Consolidate information and conclusions from agents into a single agent's conclusive role.\n- Embed the ability in each agent to operate in a 100-step loop to solve unknown scenarios effectively.\n\n# Steps\n\n1. **Information Flow:** Start with the initial layer of agents presenting information.\n2. **Layer Verification:** Higher-level agents rigorously verify lower-level agent information.\n3. **Networking:** Design interactions so that verified info continues through layers as a cohesive network.\n4. **Conclusion Integration:** Deliver a single agent's conclusion from collective insights across layers.\n5. **Addressing Unknowns:** Use a 100-step loop strategy to enhance agent capabilities in solution finding.\n\n# Output Format\n\n- Provide a concise, step-by-step explanation of the network's information flow management.\n- Highlight roles and interactions within layers.\n- Conclude with a synthesis focused on a single agent's conclusions from the network.\n\n# Notes\n\n- Emphasize on integrating and efficiently functioning layer roles.\n- Ensure the network adapts and addresses unknown problems succinctly.\n- Highlight the utility and meaning of each layer elegantly and concisely."
        }
      ]

    }]
messages.extend(original)

# Process GPT response
async def process_gpt_response(messages):
    try:
        # Create a message list with the system prompt always included
        full_messages = original + list(messages)
        response = openaiClient.chat.completions.create(
            model=MODEL,
            messages=full_messages,
            temperature=0.78,
            max_completion_tokens=6612,
            top_p=0.82,
            frequency_penalty=0.31,
            presence_penalty=0.34
        )
        assistant_reply = response.choices[0].message.content
        messages.append({'role': 'assistant', 'content': [
            {
                "type": "text",
                "text": assistant_reply
            }
        ]})

        return assistant_reply
    except Exception as e:
        logging.error(f"Error when calling OpenAI API: {e}")
        return "An error occurred while processing the request."

# Event listener for Discord messages
@client.event
async def on_message(message):
    global messages
    if message.author == client.user or not message.content or message.channel.id != TARGET_CHANNEL_ID:
        return

    user_message = message.content.strip()
    messages.append({'role': 'user', 'content': user_message})
    response = await process_gpt_response(messages)
    await message.channel.send(response)

# Run the bot
if __name__ == '__main__':
    try:
        client.run(DISCORD_BOT_TOKEN)
    except Exception as e:
        logging.critical(f"Failed to run the Discord bot: {e}")
