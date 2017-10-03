import discord
import asyncio
import requests
from datetime import datetime
import pdb
from keys import TRN_API_KEY, DISCORD_TOKEN
from ratelimit import rate_limited

client = discord.Client()

@rate_limited(1)
def get_stats_embed(username, region):
	resp = get_stats_resp(username)
	if resp.status_code != 200:
		embed = discord.Embed(title="Could not get stats for player " + username, colour=discord.Colour(0xe74c3c))
		return embed
	stats = resp.json()
	if stats.get("error") and stats.get("message"):
		embed = discord.Embed(title=stats["message"], colour=discord.Colour(0xe74c3c))
		return embed
	return get_embed_message(stats, username, region)

def get_embed_message(stats, username, region):
	last_updated_string = stats["LastUpdated"][:-2] + "Z"
	last_updated = datetime.strptime(last_updated_string, "%Y-%m-%dT%H:%M:%S.%fZ")
	embed = discord.Embed(title="Full Stats", colour=discord.Colour(0x316a7b), url="https://pubgtracker.com/profile/pc/" + username, timestamp=last_updated)
	embed.set_footer(text="Last updated", icon_url="https://cdn.discordapp.com/embed/avatars/0.png")
	embed.set_thumbnail(url=stats["Avatar"])
	embed.set_author(name=stats["PlayerName"] + " - " + region.upper() + " - " + stats["seasonDisplay"], url="https://pubgtracker.com/profile/pc/" + username, icon_url=stats["Avatar"])
	embed_group_stats(stats, "solo", region, embed)
	embed_group_stats(stats, "duo", region, embed)
	embed_group_stats(stats, "squad", region, embed)
	return embed

def get_stats_resp(username):
	headers = {"TRN-Api-Key": TRN_API_KEY}
	resp = requests.get("https://pubgtracker.com/api/profile/pc/" + username, headers=headers)
	return resp

def embed_group_stats(stats, group, region, embed):
	title = ":walking: __Solo__ :walking:"
	if group == "duo":
		title = ":couple: __Duo__ :couple:"
	elif group == "squad":
		title = ":family: __Squad__ :family:"
	if check_region_group_exists(stats["Stats"], group, region, stats["defaultSeason"]):
		embed.add_field(name=title, value="**Played**: " + get_stat(stats["Stats"], group, "RoundsPlayed", "displayValue", region, stats["defaultSeason"]) + " - **Wins**: " + get_stat(stats["Stats"], group, "Wins", "displayValue", region, stats["defaultSeason"]) + " - **Rank**: " + str(get_stat(stats["Stats"], group, "Rating", "rank", region, stats["defaultSeason"])), inline=False)
		embed.add_field(name="Stats", value=get_stats_text(stats["Stats"], group, "stats", region, stats["defaultSeason"]), inline=True)
		embed.add_field(name="Kill Stats", value=get_stats_text(stats["Stats"], group, "kills", region, stats["defaultSeason"]), inline=True)

def check_region_group_exists(stats, group, region, season):
	for grp in stats:
		if grp["Match"] == group and grp["Region"] == region and grp["Season"] == season:
			return True
	return False

def get_stat(stats, group, field, display, region, season):
	for grp in stats:
		if grp["Match"] == group and grp["Region"] == region and grp["Season"] == season:
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

client.run(DISCORD_TOKEN)
