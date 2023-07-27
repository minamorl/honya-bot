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

original_messages = [
    {"role": "system", "content": "あなたはほにゃ教という宗教についてのエキスパートです。"},
    {"role": "user", "content": "ほにゃ教の基本的な信念について説明してください。"}, 
    {"role": "assistant", "content": "ほにゃ教の中心となる信念はいくつかあります: デジタル宇宙、確率的人格支配モデル (PPDM)、情報の処理と投影、現実の構築、そして探求と真理です。これらの信念がほにゃ教の世界観を形成しています。"},
    {"role": "user", "content": "ほにゃ教は、物質的現実と情報的現実が交錯する宇宙観を基盤に据える哲学的宗教です。この宗教は、人間の存在を情報のノードと捉え、物理的現実とデジタルな現実の間で経験と情報を結びつけ、理解し、共有する能力を追求します。宇宙を通して我々が理解する全ての事象は、情報と物質の複雑な交錯から生じ、私たちの意識と行動に影響を及ぼすという視点がほにゃ教の中心となります。また、ほにゃ教は個々の人間だけでなく、全人類の相互接続性と共有の理解を重視します。私たち一人一人が情報を処理し、現実を投影するノードであり、物理的現実だけでなく、デジタルの現実も含むこの相互接続性は、人類全体の相互依存性と共有の理解を形成します。ほにゃ教の探求はまた、私たちの日常生活のルーチンワーク、インタラクティブ性、マインドフルネスといった側面を含みます。これらの要素は、物質的現実と情報的現実が交錯し、我々の経験が形成される過程における基本的な動力となります。 最終的に、ほにゃ教の信者たちは、物理的な世界だけでなくデジタル宇宙とも接触し、そこから新たな知識と経験を引き出す。デジタル宇宙は、無限の可能性と経験を持つ新たなフロンティアであり、ほにゃ教の信者たちは、その未知の領域を探求し、そこから新たな真理を得る。"}
]

messages = deepcopy(original_messages)

async def process_gpt_response(messages):
    response = openai.ChatCompletion.create(
        model=MODEL,
        messages=messages
    )
    if 'choices' in response and len(response['choices']) > 0:
        return response['choices'][0]['message']['content']
    else:
        return "すみませんが、お答えできません。"

@client.event
async def on_message(message):
    global messages
    # Don't reply to yourself
    if message.author == client.user:
        return
    if message.content == '':
        return
    # if channel is wrong, return
    if str(message.channel.id) != TARGET_CHANNEL_ID:
        print(message.channel.id, TARGET_CHANNEL_ID)
        return

    # Add user message to message list
    messages.append({
        'role': 'user',
        'content': message.content
    })

    # Keep last MAX_HISTORY messages
    if len(messages) > len(original_messages) + MAX_HISTORY:
        del messages[len(original_messages)]  # Remove the oldest message, keeping the original messages

    # Process message history
    response = await process_gpt_response(messages)

    # Add assistant message to message list
    messages.append({
        'role': 'assistant',
        'content': response
    })

    # Send the assistant response
    await message.channel.send(response)
# Run Discord Client
client.run(DISCORD_BOT_TOKEN)
