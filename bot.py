import os
import re
import json
import discord
from discord.ext import tasks
import aiohttp

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
ACCOUNT_ID = os.getenv("ACCOUNT_ID")
API_KEY = os.getenv("API_KEY")
MAX_PLAYERS = 60

intents = discord.Intents.default()
client = discord.Client(intents=intents)

def extract_player_count(payload):
    if isinstance(payload, dict):
        for key in ("players", "Players", "playercount", "PlayerCount", "currentPlayers", "CurrentPlayers", "onlinePlayers", "OnlinePlayers"):
            value = payload.get(key)
            if value is not None:
                try:
                    return int(value)
                except (TypeError, ValueError):
                    match = re.search(r"\d+", str(value))
                    if match:
                        return int(match.group())
        for value in payload.values():
            result = extract_player_count(value)
            if result is not None:
                return result

    elif isinstance(payload, list):
        for item in payload:
            result = extract_player_count(item)
            if result is not None:
                return result

    else:
        match = re.search(r"\b(\d{1,3})\b", str(payload))
        if match:
            return int(match.group(1))

    return None

@tasks.loop(minutes=2)
async def update_channel():
    try:
         url = f"https://api.scpslgame.com/serverinfo.php?id={ACCOUNT_ID}&key={API_KEY}&players=true"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                data = await resp.json(content_type=None)

        players = "0/60"
        online = False

        servers = data.get("servers") or data.get("Servers") or []

        for server in servers:
            server_id = str(
                server.get("ServerID")
                or server.get("server_id")
                or server.get("id")
                or ""
            )

            if server_id == "103398" or "UNDERGROUND-PROJECT" in str(server).upper():
                online = True

                pc = (
                    server.get("players_count")
                    or server.get("PlayersCount")
                    or server.get("playersCount")
                    or {}
                )

                if isinstance(pc, dict):
                    current = pc.get("current_players") or pc.get("currentPlayers") or pc.get("current") or 0
                    maximum = pc.get("max_players") or pc.get("maxPlayers") or pc.get("max") or 60
                    players = f"{current}/{maximum}"
                else:
                    players = str(server.get("Players") or server.get("players") or "0/60")

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
