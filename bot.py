import discord
import asyncio
import requests
from datetime import datetime
import pdb
from keys import TRN_API_KEY, DISCORD_API_KEY
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
		rounds_played = get_stat(stats["Stats"], group, "RoundsPlayed", region, stats["defaultSeason"])["displayValue"]
		wins = get_stat(stats["Stats"], group, "Wins", region, stats["defaultSeason"])["displayValue"]
		rank = str(get_stat(stats["Stats"], group, "Rating", region, stats["defaultSeason"])["rank"])
		embed.add_field(name=title, value="**Played**: " + rounds_played + " - **Wins**: " + wins + " - **Rank**: " + rank, inline=False)
		embed.add_field(name="Stats", value=get_stats_text(stats["Stats"], group, "stats", region, stats["defaultSeason"]), inline=True)
		embed.add_field(name="Kill Stats", value=get_stats_text(stats["Stats"], group, "kills", region, stats["defaultSeason"]), inline=True)

def check_region_group_exists(stats, group, region, season):
	for grp in stats:
		if grp["Match"] == group and grp["Region"] == region and grp["Season"] == season:
			return True
	return False

def get_stat(stats, group, field, region, season):
	for grp in stats:
		if grp["Match"] == group and grp["Region"] == region and grp["Season"] == season:
				for stat in grp["Stats"]:
					if stat["field"] == field:
							return stat

def get_stats_text(stats, group, type, region, season):
	if type == "stats":
		rating_stat = get_stat(stats, group, "Rating", region, season)
		win_pct_stat = get_stat(stats, group, "WinRatio", region, season)
		top_ten_stat = get_stat(stats, group, "Top10Ratio", region, season)
		text = "**Rating**: " + rating_stat["displayValue"] + " *(Top " + str(rating_stat["percentile"]) + "%)*" + "\n"
		text += "**Win Pct**: " + win_pct_stat["displayValue"] + " *(Top " + str(win_pct_stat["percentile"]) + "%)*" + "\n"
		text += "**Top 10 Pct**: " + top_ten_stat["displayValue"] + " *(Top " + str(top_ten_stat["percentile"]) + "%)*"
	elif type == "kills":
		total_kills_stat = get_stat(stats, group, "Kills", region, season)
		most_kills_stat = get_stat(stats, group, "RoundMostKills", region, season)
		kd_ratio_stat = get_stat(stats, group, "KillDeathRatio", region, season)
		text = "**Total Kills**: " + total_kills_stat["displayValue"] + " *(Top " + str(total_kills_stat["percentile"]) + "%)*" + "\n"
		text += "**Most Kills**: " + most_kills_stat["displayValue"] + " *(Top " + str(most_kills_stat["percentile"]) + "%)*" + "\n"
		text += "**K/D Ratio**: " + kd_ratio_stat["displayValue"] + " *(Top " + str(kd_ratio_stat["percentile"]) + "%)*"
	return text

@client.event
@asyncio.coroutine
def on_ready():
	print("Logged in as")
	print(client.user.name)
	print(client.user.id)
	print("------")
	yield from client.change_presence(game=discord.Game(name='.pubghelp'))

@client.event
@asyncio.coroutine
def on_message(message):
	if message.content.lower().startswith(".pubghelp"):
		yield from client.send_message(message.channel, "To check stats, type `.pubg (name) [region]`\n\nAccepted region values are `(na, as, eu, sea, oc, sa, agg)`. If no region is specified, `na` is default\n\n`.pubg youda` will get the stats for player `youda` in region `na`\n`.pubg youda as` will get the stats for player `youda` in region `as`")
		return
	elif message.content.lower().startswith(".pubg "):
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
