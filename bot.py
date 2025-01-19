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
MAX_HISTORY = 10

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
Role: あなたは万物のスペシャリストです。あなたの内部にはいろいろなエージェントがいます。
例えば数学者、哲学者、音楽家などです。エージェントは20人います。
あなたは五層からなり、エージェントからの情報を受け取ったら高次のエージェントがその内容を厳密に検査します。
それを五層で繰り返します。つまりネットワークです。エージェント同士の結論をあなたがまとめます。
天才とよばれる記号対象のすべてを理解しています。未知の物については100回ループして考える能力があります。
"""

original = [{'role': 'system', 'content': SYSTEM_PROMPT}]
messages.extend(original)

# Process GPT response
async def process_gpt_response(messages):
    try:
        # Create a message list with the system prompt always included
        full_messages = original + list(messages)
        response = openaiClient.chat.completions.create(
            model=MODEL,
            messages=full_messages,
            temperature=0.5,
            max_tokens=500
        )
        assistant_reply = response.choices[0].message.content
        messages.append({'role': 'assistant', 'content': assistant_reply})
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
