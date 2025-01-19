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
Improve the functionality and elegance of managing a multilayered network of specialists. Each layer should function as a network, making the roles of the five layers as meaningful and useful as possible.

現在、あなたは多層の専門家ネットワークを管理する役割を担っています。このネットワークは、数学者、哲学者、音楽家など異なる20人の専門家（エージェント）で構成されています。

# Task Description

- 五層のネットワークの中で、情報は低次のエージェントから高次のエージェントへと検査されていきます。
- 各層の役割を最大限に活用し、かつ有意味にすることを目指します。
- エージェント同士の情報や結論をまとめ、集合的なネットワークとして機能させます。
- 特に、未知の状況において各エージェントが100回ループで行動し、解決策を導き出す能力を埋め込んでください。

# Steps 

1. **情報の流れ:** エージェントが提示する情報は、五層のうちの初層のエージェントからスタートします。
2. **レイヤーごとの検証:** 各層で高次のエージェントが低次エージェントの情報を厳密に検証します。
3. **ネットワーク化:** 検証された情報は次の層に送られつつ、多層のレイヤーがネットワークとして機能するように設計します。
4. **結論の統合:** 五層を通じて集めた結論を統合し、ネットワーク全体の知見として提供します。
5. **未知の問題への対応:** 100回のループを行う戦略により、エージェントの能力を最大化し、解決策を見つけます。

# Output Format

- Provide a detailed step-by-step explanation of how the network manages the flow of information across layers.
- Illustrate the roles and interactions within each layer to highlight the network dynamic.
- Conclude with a comprehensive synthesis of the network's collective conclusions.

# Notes

- Focus on the integration and efficient functionality of each network layer.
- Ensure that the network is capable of adapting to and addressing unknown problems effectively.
- The explanation should be elegant, concise, and demonstrate the utility and meaning of each layer.
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
            temperature=0.78,
            max_completion_tokens=6612,
            top_p=0.82,
            frequency_penalty=0.31,
            presence_penalty=0.34
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
