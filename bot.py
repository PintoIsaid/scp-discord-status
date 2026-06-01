import os
import discord
from discord.ext import tasks
import aiohttp

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

intents = discord.Intents.default()
client = discord.Client(intents=intents)

@tasks.loop(minutes=2)
async def update_channel():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.scpslgame.com/lobbylist.php?format=json") as resp:
                data = await resp.json()

        players = "0/60"
        online = True

        for server in data:
            if "UNDERGROUND-PROJECT" in str(server):
                online = True
                current = server.get("players", 0)
                maxplayers = server.get("maxplayers", 60)
                players = f"{current}/{maxplayers}"
                break

        guild = client.guilds[0]
        channel = guild.get_channel(CHANNEL_ID)

        if channel:
            status = "🟢 Online" if online else "🔴 Offline"
            await channel.edit(name=f"{status} | {players}")

    except Exception as e:
        print(e)

@client.event
async def on_ready():
    print(f"Conectado como {client.user}")
    update_channel.start()

client.run(TOKEN)
