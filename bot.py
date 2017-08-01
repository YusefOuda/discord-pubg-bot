import discord
import asyncio
import requests
import datetime
import pdb
from keys import TRN_API_KEY, DISCORD_API_KEY
from ratelimit import rate_limited

client = discord.Client()

@rate_limited(1)
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
	embed.set_footer(text="yusefouda.com/discord-pubg-bot", icon_url="https://cdn.discordapp.com/embed/avatars/0.png")
	embed.set_thumbnail(url=json_stats["Avatar"])
	embed.set_author(name=json_stats["PlayerName"] + " - " + region.upper(), url="https://pubgtracker.com/profile/pc/" + username, icon_url=json_stats["Avatar"])
	if check_region_group_exists(json_stats["Stats"], "solo", region, json_stats["Season"]):
		embed.add_field(name=":walking: __Solo__ :walking:", value="**Played**: " + get_stat(json_stats["Stats"], "solo", "RoundsPlayed", "displayValue", region, json_stats["Season"]) + " - **Wins**: " + get_stat(json_stats["Stats"], "solo", "Wins", "displayValue", region) + " - **Rank**: " + str(get_stat(json_stats["Stats"], "solo", "Rating", "rank", region, json_stats["Season"])), inline=False)
		embed.add_field(name="Stats", value=get_stats_text(json_stats["Stats"], "solo", "stats", region, json_stats["Season"]), inline=True)
		embed.add_field(name="Kill Stats", value=get_stats_text(json_stats["Stats"], "solo", "kills", region, json_stats["Season"]), inline=True)
	if check_region_group_exists(json_stats["Stats"], "duo", region, json_stats["Season"]):
		embed.add_field(name=":couple: __Duo__ :couple:", value="**Played**: " + get_stat(json_stats["Stats"], "duo", "RoundsPlayed", "displayValue", region, json_stats["Season"]) + " - **Wins**: " + get_stat(json_stats["Stats"], "duo", "Wins", "displayValue", region) + " - **Rank**: " + str(get_stat(json_stats["Stats"], "duo", "Rating", "rank", region, json_stats["Season"])), inline=False)
		embed.add_field(name="Stats", value=get_stats_text(json_stats["Stats"], "duo", "stats", region, json_stats["Season"]), inline=True)
		embed.add_field(name="Kill Stats", value=get_stats_text(json_stats["Stats"], "duo", "kills", region, json_stats["Season"]), inline=True)
	if check_region_group_exists(json_stats["Stats"], "squad", region, json_stats["Season"]):
		embed.add_field(name=":family: __Squad__ :family:", value="**Played**: " + get_stat(json_stats["Stats"], "squad", "RoundsPlayed", "displayValue", region, json_stats["Season"]) + " - **Wins**: " + get_stat(json_stats["Stats"], "squad", "Wins", "displayValue", region) + " - **Rank**: " + str(get_stat(json_stats["Stats"], "squad", "Rating", "rank", region, json_stats["Season"])), inline=False)
		embed.add_field(name="Stats", value=get_stats_text(json_stats["Stats"], "squad", "stats", region, json_stats["Season"]), inline=True)
		embed.add_field(name="Kill Stats", value=get_stats_text(json_stats["Stats"], "squad", "kills", region, json_stats["Season"]), inline=True)
	return embed

def check_region_group_exists(stats, group, region, season):
	for grp in stats:
		if grp["Match"] == group and grp["Region"] == region && grp["Season"] == season:
			return True
	return False

def get_stat(stats, group, field, display, region, season):
	for grp in stats:
		if grp["Match"] == group and grp["Region"] == region && grp["Season"] == season:
				for stat in grp["Stats"]:
					if stat["field"] == field:
							return stat[display]

def get_stats_text(stats, group, type, region, season):
	if type == "stats":
		text = "**Rating**: " + get_stat(stats, group, "Rating", "displayValue", region, season) + "\n"
		text += "**Win Pct**: " + get_stat(stats, group, "WinRatio", "displayValue", region, season) + "\n"
		text += "**Top 10 Pct**: " + get_stat(stats, group, "Top10Ratio", "displayValue", region, season)
	elif type == "kills":
		text = "**Total Kills**: " + get_stat(stats, group, "Kills", "displayValue", region, season) + "\n"
		text += "**Most Kills**: " + get_stat(stats, group, "RoundMostKills", "displayValue", region, season) + "\n"
		text += "**K/D Ratio**: " + get_stat(stats, group, "KillDeathRatio", "displayValue", region, season)
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
