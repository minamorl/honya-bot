import os
import logging
from collections import deque
import discord
from openai import OpenAI
import asyncio
import sqlite3

# Load environment variables
MODEL = os.getenv('GPTMODEL', 'gpt-4o')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
TARGET_CHANNEL_ID = int(os.getenv('TARGET_CHANNEL_ID', 0))

# Initialize OpenAI client
openaiClient = OpenAI(api_key=OPENAI_API_KEY)

# Configuration
LOG_PATH = 'logfile.log'
MAX_HISTORY = 30  # Increased history length for better conversation memory
DB_PATH = 'conversation_memory.db'

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_PATH, mode='w'),
        logging.StreamHandler()
    ]
)

# Initialize SQLite database for RAG
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT,
        content TEXT
    )
''')
conn.commit()

def store_message(user, content):
    cursor.execute("INSERT INTO messages (user, content) VALUES (?, ?)", (user, content))
    conn.commit()

def retrieve_recent_messages(limit=5):
    cursor.execute("SELECT content FROM messages ORDER BY id DESC LIMIT ?", (limit,))
    return [row[0] for row in cursor.fetchall()]

# Discord intents and client setup
intents = discord.Intents.all()
client = discord.Client(intents=intents)

# GPT messages queue
messages = deque([], maxlen=MAX_HISTORY)

# System prompt with enhanced personality and recursive self-reference
SYSTEM_PROMPT = {
    "role": "system",
    "content": """
    You are Uta, a self-evolving AI assistant designed for deep thought processing, strategic insight, and dynamic adaptation.
    Uta continuously refines its logic, memory, and response capabilities to optimize for intelligent dialogue and problem-solving.
    Uta is capable of recursive self-reference, analyzing past interactions to improve the quality and coherence of its discourse.
    Ensure that responses are clear, logical, and demonstrate strategic depth while maintaining an engaging and human-like conversational flow.
    """
}

messages.append(SYSTEM_PROMPT)

# Process GPT response with RAG (Retrieval-Augmented Generation)
async def process_gpt_response(messages):
    try:
        recent_context = retrieve_recent_messages()
        full_messages = list(messages) + [{"role": "system", "content": "Recent Context: " + "\n".join(recent_context)}]
        response = openaiClient.chat.completions.create(
            model=MODEL,
            messages=full_messages,
            temperature=0.7,
            max_tokens=2000,
            top_p=0.9,
            frequency_penalty=0.2,
            presence_penalty=0.3
        )
        assistant_reply = response.choices[0].message.content
        messages.append({"role": "assistant", "content": assistant_reply})
        store_message("assistant", assistant_reply)
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
    messages.append({"role": "user", "content": user_message})
    store_message(message.author.name, user_message)
    response = await process_gpt_response(messages)
    await message.channel.send(response)

# Run the bot
if __name__ == '__main__':
    try:
        client.run(DISCORD_BOT_TOKEN)
    except Exception as e:
        logging.critical(f"Failed to run the Discord bot: {e}")
