import os
from typing import Deque
import re

import discord
import openai
import logging
import json
from copy import deepcopy

MAX_HISTORY = 10

# Set log level
log_path = "logfile.log"
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s [%(levelname)s] %(message)s',
                    handlers=[logging.FileHandler(log_path, mode='w'), logging.StreamHandler()])

# Load config
with open('config.json', 'r') as f:
    config = json.load(f)
    MODEL             = config['MODEL'][0]
    OPENAI_API_KEY    = config['OPENAI_API_KEY'][0]
    DISCORD_BOT_TOKEN = config['DISCORD_BOT_TOKEN'][0]
    TARGET_CHANNEL_ID = config['TARGET_CHANNEL_ID'][0]

# Initialize OpenAI API
openai.api_key = OPENAI_API_KEY

# Initialize Discord Client
intents = discord.Intents.all()
client = discord.Client(intents=intents)


messages = Deque([], MAX_HISTORY)

async def process_gpt_response(messages):
    response = openai.ChatCompletion.create(
        model=MODEL,
        messages=list(messages)
        ,temperature=0.1,
    )
    if 'choices' in response and len(response['choices']) > 0:
        return response['choices'][0]['message']['content']
    else:
        return "すみませんが、お答えできません。"


async def execute_command(command):
    # stream = os.popen(command)
    # output = stream.read()
    # return output
    return

@client.event
async def on_message(message):
    global messages
    print(messages)
    # Don't reply to yourself
    if message.author == client.user:
        return
    if message.content == '':
        return
    # if channel is wrong, return
    if str(message.channel.id) != TARGET_CHANNEL_ID:
        return

    # Add user message to message list
    messages.append({
        'role': 'user',
        'content': message.content
    })

    # Process message history
    response = await process_gpt_response(messages)

    messages.append({
        'role': 'assistant',
        'content': response
    })

    await message.channel.send(response)

    #     # コマンド実行のチェック
    #     matches = re.findall(r'```?(.+?)?```', response, re.DOTALL)
    #     for cmd in matches:
    #         print(cmd)
    #         cmd = cmd.strip()
    #         cmd_response = await execute_command(cmd)
    #         response = f"Executing command: {cmd}\n{cmd_response}"
    # 
    #         # Add assistant message to message list
    #         messages.append({
    #             'role': 'assistant',
    #             'content': response
    #         })
    # 
    #         # Send the assistant response
    #         await message.channel.send(response)
    # 
client.run(DISCORD_BOT_TOKEN)
