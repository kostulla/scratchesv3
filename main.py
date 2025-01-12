import discord
from discord import app_commands
from discord.ext import commands
import random
import json
from datetime import datetime

import socket

def start_server(host, port):
    # Create a socket object
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to the specified host and port
    server_socket.bind((host, port))

    # Enable the server to listen for incoming connections (max 5 clients)
    server_socket.listen(5)

    print(f"Server started on {host}:{port}. Waiting for connections...")

    while True:
        # Accept an incoming connection
        client_socket, client_address = server_socket.accept()
        print(f"Connection from {client_address} established.")

        # Send a welcome message to the client
        client_socket.send(b"Hello, client! Welcome to the server.")

        # Receive data from the client
        data = client_socket.recv(1024)
        print(f"Received data from client: {data.decode()}")

        # Close the connection
        client_socket.close()

if __name__ == "__main__":
    start_server('127.0.0.1', 12345)  # Localhost and port 12345

# Intents and bot setup
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="/", intents=intents)

# Load user data from JSON file or initialize empty
try:
    with open("user_data.json", "r") as f:
        user_data = json.load(f)
except FileNotFoundError:
    user_data = {}

# Save user data to JSON file
def save_user_data():
    with open("user_data.json", "w") as f:
        json.dump(user_data, f, indent=4)

# Scratch categories with emojis, point ranges, and colors
SCRATCH_CATEGORIES = [
    ("<:common:1324901739102601236> **𝘾𝙊𝙈𝙈𝙊𝙉 𝙎𝙘𝙧𝙖𝙩𝙘𝙝**", (100, 199, discord.Color.red())),
    ("<:rare:1324898374654234775> **𝙍𝘼𝙍𝙀 𝙎𝙘𝙧𝙖𝙩𝙘𝙝**", (200, 299, discord.Color.green())),
    ("<:epic:1324901795503538247> **𝙀𝙋𝙄𝘾 𝙎𝙘𝙧𝙖𝙩𝙘𝙝**", (300, 399, discord.Color.purple())),
    ("<:legendary:1324899321832800257> **𝙇𝙀𝙂𝙀𝙉𝘿𝘼𝙍𝙔 𝙎𝙘𝙧𝙖𝙩𝙘𝙝**", (400, 500, discord.Color.gold())),
    ("<:declined:1325051341520764959> **𝙔𝙊𝙐 𝙇𝙤𝙨𝙩**", (-500, -100, discord.Color.dark_red())),
]

# Weights for scratch probabilities
CATEGORY_WEIGHTS = [80, 50, 27, 10, 78]

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Bot is ready and logged in as {bot.user}")

@bot.tree.command(name="scratch", description="Play & Win.")
async def scratch(interaction: discord.Interaction):
    user_id = str(interaction.user.id)

    # Initialize user data if not present
    if user_id not in user_data:
        user_data[user_id] = {"points": 0}

    # Randomly select a scratch category
    category_index = random.choices(range(len(SCRATCH_CATEGORIES)),
                                    weights=CATEGORY_WEIGHTS,
                                    k=1)[0]
    category, (min_points, max_points, embed_color) = SCRATCH_CATEGORIES[category_index]

    # Determine points
    points = random.randint(min_points, max_points)

    # Add or subtract points based on the category
    user_data[user_id]["points"] = max(0, user_data[user_id]["points"] + points)

    # Save data
    save_user_data()

    # Create embed
    embed = discord.Embed(
        title=f"{category}",
        description=f"> You {'gained' if points > 0 else 'lost'} **{abs(points)}** points!",
        color=embed_color,
        timestamp=datetime.utcnow(),
    )
    embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1325191066718310442/1325199882511974593/IMG_8240.png?ex=677aec11&is=67799a91&hm=8f95474b13b1391b1920fcae0f4218f4280f1fcbf7622ff5411d749251fdb9bf&")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="mypoints", description="View your total scratch-points.")
async def mypoints(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    points = user_data.get(user_id, {}).get("points", 0)

    embed = discord.Embed(
        title="<:coin:1325068743126159390> 𝙈𝙔 𝙋𝙤𝙞𝙣𝙩𝙨",
        description=f"**You have a total of `{points}` points available.**",
        color=discord.Color.blue(),
        timestamp=datetime.utcnow(),
    )
    embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1325191066718310442/1325199882511974593/IMG_8240.png?ex=677aec11&is=67799a91&hm=8f95474b13b1391b1920fcae0f4218f4280f1fcbf7622ff5411d749251fdb9bf&")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="scratch-rewards", description="View scratch's rewards!")
async def scratch_rewards(interaction: discord.Interaction):
    rewards = [
        "<:giveaway:1322925630697771018> **25% Discount**",
"**>20.000 points",
        "<a:discordbot:1304744338210816000> **Discord Bot Source!**",
    ]
    rewards_text = "\n".join(rewards)

    embed = discord.Embed(
        title="<:epic:1324901795503538247> **SCRATCH REWARDS**",
        description=rewards_text,
        color=discord.Color.gold(),
        timestamp=datetime.utcnow(),
    )
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1325191066718310442/1325199882511974593/IMG_8240.png?ex=677aec11&is=67799a91&hm=8f95474b13b1391b1920fcae0f4218f4280f1fcbf7622ff5411d749251fdb9bf&")
    await interaction.response.send_message(embed=embed, ephemeral=True)