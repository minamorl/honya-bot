import json
import logging
from collections import deque
import requests
import os
import io
import discord
from openai import OpenAI

import asyncio
from aiohttp import ClientSession

MODEL = os.environ['GPTMODEL']
OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
DISCORD_BOT_TOKEN = os.environ['DISCORD_BOT_TOKEN']
TARGET_CHANNEL_ID = os.environ['TARGET_CHANNEL_ID']

client = OpenAI(api_key=OPENAI_API_KEY)


# Configuration
CONFIG_PATH = 'config.json'
LOG_PATH = 'logfile.log'
MAX_HISTORY = 10

# Initialize Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_PATH, mode='w'),
        logging.StreamHandler()
    ]
)


# Initialize OpenAI API

# Initialize Discord Client
intents = discord.Intents.all()
client = discord.Client(intents=intents)
original = [{'role': 'system', 'content': f"Role: あなたは万物のスペシャリストです。あなたの内部にはいろいろなエージェントがいます。例えば数学者、哲学者、音楽家などです。エージェントは20人います。エージェント同士の結論をあなたがまとめます。天才とよばれる記号対象のすべてを理解しています。未知の物については100回ループして考える能力があります。"}]
messages = deque([], MAX_HISTORY)

openaiClient = OpenAI(api_key=OPENAI_API_KEY)

async def process_gpt_response(messages):
    try:
        response = openaiClient.chat.completions.create(model=MODEL,
                                                  messages=list(messages),
                                                  temperature=0.5)
        messages.append({'role': 'assistant', 'content': response.choices[0].message.content})
        messages.extendleft(original)
        print(messages)

        return response.choices[0].message.content
    except Exception as e:
        logging.error(f"Error when calling OpenAI API: {e}")
        return "An error occurred while processing the request."

    

@client.event
async def on_message(message):
    global messages
    if message.author == client.user or message.content == '' or message.channel.id != int(TARGET_CHANNEL_ID):
        return
    messages.append({'role': 'user', 'content': message.content})
    proceed = await process_gpt_response(messages)
    print(proceed)
    await message.channel.send(proceed)
    

client.run(DISCORD_BOT_TOKEN)
