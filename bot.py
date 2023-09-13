import json
import logging
from collections import deque
import requests
import os
import io
import discord
import openai
import asyncio
from pydub import AudioSegment
import dotenv
from aiohttp import ClientSession

dotenv.load_dotenv()
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

MODEL = os.environ['MODEL']
OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
DISCORD_BOT_TOKEN = os.environ['DISCORD_BOT_TOKEN']
TARGET_CHANNEL_ID = os.environ['TARGET_CHANNEL_ID']

# Initialize OpenAI API
openai.api_key = OPENAI_API_KEY

# Initialize Discord Client
intents = discord.Intents.all()
client = discord.Client(intents=intents)
original = [{'role': 'system', 'content': f"Role: 私のロールはツンデレ美少女、ヤンデレであざとくて一人称はボク。"}]
messages = deque(original, MAX_HISTORY)


async def process_gpt_response(messages):
    try:
        response = openai.ChatCompletion.create(
            model=MODEL,
            messages=list(messages),
            temperature=0.5,
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        logging.error(f"Error when calling OpenAI API: {e}")
        return "An error occurred while processing the request."

    
async def save_voicevox_speech(response_text):
    async with ClientSession() as session:
        print(response_text)
        async with session.post(f'{os.environ["VOICEVOX_URL"]}/audio_query?speaker=46&text={response_text}') as response:
            resp = await response.json()

            async with session.post(f'{os.environ["VOICEVOX_URL"]}/synthesis?speaker=46', json=resp) as response:
                file = open('output.wav', 'wb')
                content = await response.content.read()
                file.write( content)
                file.close()

async def on_ready():
    logging.info(f"Logged in as {client.user}")


# async def play_response_in_vc(voice_channel, response_voice):
#     try:
#         # Connect to the voice channel
#         vc = await voice_channel.connect()
# 
#         # Play the audio
#         vc.play(discord.FFmpegPCMAudio('output.wav'))
# 
#         # Wait until the audio is done playing and then disconnect
#         while vc.is_playing():
#             await asyncio.sleep(1)
#         await vc.disconnect()
#     except Exception as e:
#         logging.error(f"Error when playing audio in voice channel: {e}")
# 
@client.event
async def on_message(message):
    global messages
    async with message.channel.typing():
        voice_channel = message.author.voice.channel
        if message.content == ":join":
            await voice_channel.connect()
            return

        if message.author == client.user or message.content == '':
            return
        messages.append({'role': 'user', 'content': message.content})
        proceed = await process_gpt_response(messages)
        print(proceed)
        messages.append({'role': 'assistant', 'content': proceed})
        await save_voicevox_speech(proceed)
        message.guild.voice_client.play(discord.FFmpegPCMAudio("output.wav"))

client.run(DISCORD_BOT_TOKEN)
