import discord
import asyncio
import requests
import datetime
import pdb
from keys import TRN_API_KEY, DISCORD_API_KEY

client = discord.Client()

def get_stats_embed(username, region):
	print(username)
	headers = {"TRN-Api-Key": TRN_API_KEY}
	r = requests.get("https://pubgtracker.com/api/profile/pc/" + username, headers=headers)
	if r.status_code != 200:
		embed = discord.Embed(title="Could not get stats for player " + username, colour=discord.Colour(0xe74c3c))
		return embed
	json = r.json()
	embed = discord.Embed(title="Full Stats", colour=discord.Colour(0x316a7b), url="https://pubgtracker.com/profile/pc/" + username, timestamp=datetime.datetime.utcnow())
	embed.set_footer(text="Bot created by Yusef Ouda", icon_url="https://cdn.discordapp.com/embed/avatars/0.png")
	embed.set_thumbnail(url=json["Avatar"])
	embed.set_author(name=username, url="https://pubgtracker.com/profile/pc/" + username, icon_url=json["Avatar"])
	embed.add_field(name=":walking: __Solo__ :walking:", value="**Wins**: " + get_stat(json["Stats"], "solo", "Wins", "displayValue", region) + " - **Rank**: " + str(get_stat(json["Stats"], "solo", "Rating", "rank", region)), inline=False)
	embed.add_field(name="Stats", value=get_stats_text(json["Stats"], "solo", "stats", region), inline=True)
	embed.add_field(name="Kill Stats", value=get_stats_text(json["Stats"], "solo", "kills", region), inline=True)
	embed.add_field(name=":couple: __Duo__ :couple:", value="**Wins**: " + get_stat(json["Stats"], "duo", "Wins", "displayValue", region) + " - **Rank**: " + str(get_stat(json["Stats"], "duo", "Rating", "rank", region)), inline=False)
	embed.add_field(name="Stats", value=get_stats_text(json["Stats"], "duo", "stats", region), inline=True)
	embed.add_field(name="Kill Stats", value=get_stats_text(json["Stats"], "duo", "kills", region), inline=True)
	embed.add_field(name=":family: __Squad__ :family:", value="**Wins**: " + get_stat(json["Stats"], "squad", "Wins", "displayValue", region) + " - **Rank**: " + str(get_stat(json["Stats"], "squad", "Rating", "rank", region)), inline=False)
	embed.add_field(name="Stats", value=get_stats_text(json["Stats"], "squad", "stats", region), inline=True)
	embed.add_field(name="Kill Stats", value=get_stats_text(json["Stats"], "squad", "kills", region), inline=True)
	return embed

def get_stat(stats, group, field, display, region):
	for grp in stats:
		if grp["Match"] == group and grp["Region"] == region:
			for stat in grp["Stats"]:
				if stat["field"] == field:
					return stat[display]

def get_stats_text(stats, group, type, region):
	if type == "stats":
		text = "**Rating**: " + get_stat(stats, group, "Rating", "displayValue") + "\n"
		text += "**Win Pct**: " + get_stat(stats, group, "WinRatio", "displayValue") + "\n"
		text += "**Top 10 Pct**: " + get_stat(stats, group, "Top10Ratio", "displayValue")
	elif type == "kills":
		text = "**Total Kills**: " + get_stat(stats, group, "Kills", "displayValue") + "\n"
		text += "**Most Kills**: " + get_stat(stats, group, "RoundMostKills", "displayValue") + "\n"
		text += "**K/D Ratio**: " + get_stat(stats, group, "KillDeathRatio", "displayValue")
	return text
	
@client.event
@asyncio.coroutine
def on_ready():
	print("Logged in as")
	print(client.user.name)
	print(client.user.id)
	print("------")

@client.event
@asyncio.coroutine
def on_message(message):
	if message.content.lower().startswith("!stats"):
		text = message.content.split(" ")
		region = "na"
		if len(text) < 2:
			yield from client.send_message(message.channel, "Please supply a username (e.g. !stats youda)")
		if len(text) == 3:
			region = text[2]
		yield from client.send_message(message.channel, embed=get_stats_embed(text[1], region))

client.run(DISCORD_API_KEY)
