import discord
import asyncio
import requests
import datetime
import pdb
from keys import TRN_API_KEY, DISCORD_API_KEY

client = discord.Client()

def get_stats_embed(username, region):
	headers = {"TRN-Api-Key": TRN_API_KEY}
	resp = requests.get("https://pubgtracker.com/api/profile/pc/" + username, headers=headers)
	if resp.status_code != 200:
		embed = discord.Embed(title="Could not get stats for player " + username, colour=discord.Colour(0xe74c3c))
		return embed
	json_stats = resp.json()
	if json_stats.get("error") and json_stats.get("message"):
		embed = discord.Embed(title=json_stats["message"], colour=discord.Colour(0xe74c3c))
		return embed
	embed = discord.Embed(title="Full Stats", colour=discord.Colour(0x316a7b), url="https://pubgtracker.com/profile/pc/" + username, timestamp=datetime.datetime.utcnow())
	embed.set_footer(text="http://yusefouda.com/discord-pubg-bot/", icon_url="https://cdn.discordapp.com/embed/avatars/0.png")
	embed.set_thumbnail(url=json_stats["Avatar"])
	embed.set_author(name=username + " - " + region.upper(), url="https://pubgtracker.com/profile/pc/" + username, icon_url=json_stats["Avatar"])
	if check_region_group_exists(json_stats["Stats"], "solo", region):
		embed.add_field(name=":walking: __Solo__ :walking:", value="**Played**: " + get_stat(json_stats["Stats"], "solo", "RoundsPlayed", "displayValue", region) + "- **Wins**: " + get_stat(json_stats["Stats"], "solo", "Wins", "displayValue", region) + " - **Rank**: " + str(get_stat(json_stats["Stats"], "solo", "Rating", "rank", region)), inline=False)
		embed.add_field(name="Stats", value=get_stats_text(json_stats["Stats"], "solo", "stats", region), inline=True)
		embed.add_field(name="Kill Stats", value=get_stats_text(json_stats["Stats"], "solo", "kills", region), inline=True)
	if check_region_group_exists(json_stats["Stats"], "duo", region):
		embed.add_field(name=":couple: __Duo__ :couple:", value="**Played**: " + get_stat(json_stats["Stats"], "duo", "RoundsPlayed", "displayValue", region) + "- **Wins**: " + get_stat(json_stats["Stats"], "duo", "Wins", "displayValue", region) + " - **Rank**: " + str(get_stat(json_stats["Stats"], "duo", "Rating", "rank", region)), inline=False)
		embed.add_field(name="Stats", value=get_stats_text(json_stats["Stats"], "duo", "stats", region), inline=True)
		embed.add_field(name="Kill Stats", value=get_stats_text(json_stats["Stats"], "duo", "kills", region), inline=True)
	if check_region_group_exists(json_stats["Stats"], "squad", region):
		embed.add_field(name=":family: __Squad__ :family:", value="**Played**: " + get_stat(json_stats["Stats"], "squad", "RoundsPlayed", "displayValue", region) + "- **Wins**: " + get_stat(json_stats["Stats"], "squad", "Wins", "displayValue", region) + " - **Rank**: " + str(get_stat(json_stats["Stats"], "squad", "Rating", "rank", region)), inline=False)
		embed.add_field(name="Stats", value=get_stats_text(json_stats["Stats"], "squad", "stats", region), inline=True)
		embed.add_field(name="Kill Stats", value=get_stats_text(json_stats["Stats"], "squad", "kills", region), inline=True)
	return embed

def check_region_group_exists(stats, group, region):
	for grp in stats:
		if grp["Match"] == group and grp["Region"] == region:
			return True
	return False

def get_stat(stats, group, field, display, region):
	for grp in stats:
		if grp["Match"] == group and grp["Region"] == region:
				for stat in grp["Stats"]:
					if stat["field"] == field:
							return stat[display]

def get_stats_text(stats, group, type, region):
	if type == "stats":
		text = "**Rating**: " + get_stat(stats, group, "Rating", "displayValue", region) + "\n"
		text += "**Win Pct**: " + get_stat(stats, group, "WinRatio", "displayValue", region) + "\n"
		text += "**Top 10 Pct**: " + get_stat(stats, group, "Top10Ratio", "displayValue", region)
	elif type == "kills":
		text = "**Total Kills**: " + get_stat(stats, group, "Kills", "displayValue", region) + "\n"
		text += "**Most Kills**: " + get_stat(stats, group, "RoundMostKills", "displayValue", region) + "\n"
		text += "**K/D Ratio**: " + get_stat(stats, group, "KillDeathRatio", "displayValue", region)
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
	if message.content.lower().startswith(".pubg"):
		text = " ".join(message.content.split()).split()
		region = "na"
		if len(text) < 2:
			yield from client.send_message(message.channel, "Please supply a username (e.g. !stats youda)")
			return
		if len(text) == 3:
			region = text[2].lower()
		if region not in ["na", "as", "eu", "sea", "oc", "agg", "sa"]:
			yield from client.send_message(message.channel, "Invalid region " + region + ". Accepted values are (na, as, eu, sea, oc, sa, agg)")
			return
		yield from client.send_message(message.channel, embed=get_stats_embed(text[1], region))

client.run(DISCORD_API_KEY)
