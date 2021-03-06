import discord
import asyncio
import requests
import aiohttp
from datetime import datetime
import pdb
from keys import TRN_API_KEY, DISCORD_TOKEN
from ratelimit import rate_limited

client = discord.Client()

@asyncio.coroutine
@rate_limited(1)
def get_stats_embed(username, region, game_type, group):
    resp = yield from get_stats_resp(username)
    if resp.status != 200:
        embed = discord.Embed(title="Could not get stats for player " + username, colour=discord.Colour(0xe74c3c))
        return embed
    stats = yield from resp.json()
    if stats.get("error") and stats.get("message"):
        embed = discord.Embed(title=stats["message"], colour=discord.Colour(0xe74c3c))
        return embed
    if stats.get("error"):
        embed = discord.Embed(title=stats["error"], colour=discord.Colour(0xe74c3c))
        return embed
    return get_embed_message(stats, username, region, game_type, group)

def get_embed_message(stats, username, region, game_type, group):
    has_stats = False
    last_updated_string = stats["LastUpdated"][:-2] + "Z"
    last_updated = datetime.strptime(last_updated_string, "%Y-%m-%dT%H:%M:%S.%fZ")
    embed = discord.Embed(title="Full Stats", colour=discord.Colour(0x316a7b), url="https://pubgtracker.com/profile/pc/" + username, timestamp=last_updated)
    embed.set_footer(text="Last updated", icon_url="https://cdn.discordapp.com/embed/avatars/0.png")
    embed.set_thumbnail(url=stats["Avatar"])
    embed.set_author(name=stats["PlayerName"] + " - " + game_type.upper() + " - " + region.upper() + " - " + stats["seasonDisplay"], url="https://pubgtracker.com/profile/pc/" + username, icon_url=stats["Avatar"])
    solo_game_type = "solo-fpp" if game_type == "fpp" else  "solo"
    duo_game_type = "duo-fpp" if game_type == "fpp" else  "duo"
    squad_game_type = "squad-fpp" if game_type == "fpp" else  "squad"
    if "solo" in group:
        has_stats = embed_group_stats(stats, solo_game_type, region, embed)
    if "duo" in group:
        has_stats = embed_group_stats(stats, duo_game_type, region, embed)
    if "squad" in group:
        has_stats = embed_group_stats(stats, squad_game_type, region, embed)

    if has_stats == False:
        embed = discord.Embed(title="Could not get stats for player: " + username + ", region: " + region + ", game type: " + game_type + ", group: " + group, colour=discord.Colour(0xe74c3c))
        return embed
    return embed

@asyncio.coroutine
def get_stats_resp(username):
    headers = {"TRN-Api-Key": TRN_API_KEY}
    r = yield from aiohttp.get("https://pubgtracker.com/api/profile/pc/" + username, headers=headers)
    return r

def embed_group_stats(stats, group, region, embed):
    title = ":walking: __Solo__ :walking:"
    if "duo" in group:
        title = ":couple: __Duo__ :couple:"
    elif "squad" in group:
        title = ":family: __Squad__ :family:"
    if check_region_group_exists(stats["Stats"], group, region, stats["defaultSeason"]):
        rounds_played = get_stat(stats["Stats"], group, "RoundsPlayed", region, stats["defaultSeason"])["displayValue"]
        wins = get_stat(stats["Stats"], group, "Wins", region, stats["defaultSeason"])["displayValue"]
        rank = str(get_stat(stats["Stats"], group, "Rating", region, stats["defaultSeason"])["rank"])
        embed.add_field(name=title, value="**Played**: " + rounds_played + " - **Wins**: " + wins + " - **Rank**: " + rank, inline=False)
        embed.add_field(name="Stats", value=get_stats_text(stats["Stats"], group, "stats", region, stats["defaultSeason"]), inline=True)
        embed.add_field(name="Kill Stats", value=get_stats_text(stats["Stats"], group, "kills", region, stats["defaultSeason"]), inline=True)
        return True
    else:
        return False

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
        text = "**Rating**: " + rating_stat["displayValue"]
        if rating_stat["percentile"]:
            text += " *(Top " + str(rating_stat["percentile"]) + "%)*"
        text += "\n"

        text += "**Win Pct**: " + win_pct_stat["displayValue"]
        if win_pct_stat["percentile"]:
            text += " *(Top " + str(win_pct_stat["percentile"]) + "%)*"
        text += "\n"

        text += "**Top 10 Pct**: " + top_ten_stat["displayValue"]
        if top_ten_stat["percentile"]:
            text += " *(Top " + str(top_ten_stat["percentile"]) + "%)*"
    elif type == "kills":
        total_kills_stat = get_stat(stats, group, "Kills", region, season)
        most_kills_stat = get_stat(stats, group, "RoundMostKills", region, season)
        kd_ratio_stat = get_stat(stats, group, "KillDeathRatio", region, season)
        text = "**Total Kills**: " + total_kills_stat["displayValue"]
        if total_kills_stat["percentile"]:
            text += " *(Top " + str(total_kills_stat["percentile"]) + "%)*"
        text += "\n"

        text += "**Most Kills**: " + most_kills_stat["displayValue"]
        if most_kills_stat["percentile"]:
            text += " *(Top " + str(most_kills_stat["percentile"]) + "%)*"
        text += "\n"

        text += "**K/D Ratio**: " + kd_ratio_stat["displayValue"]
        if kd_ratio_stat["percentile"]:
            text += " *(Top " + str(kd_ratio_stat["percentile"]) + "%)*"
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
        help_message = "To check stats, type `.pubg (name) [region] [game type] [group]`\n\nAccepted region values are `(na, as, eu, sea, oc, sa, agg)`."
        help_message += " If no region is specified, `na` is default\n\nAccepted game type values are `(tpp, fpp)`. If no game type is specified, `fpp` is default\n\n"
        help_message += "Accepted group values are `(solo, duo, squad)`. If no group is specified, all groups will be returned.\n\n"
        help_message += "`.pubg youda` will get the stats for player `youda` in region `na` for game type `fpp`\n"
        help_message += "`.pubg youda as tpp` will get the stats for player `youda` in region `as` for game type `tpp`\n"
        help_message += "`.pubg youda tpp` will get the stats for player `youda` in region `na` for gametype `tpp`\n"
        yield from client.send_message(message.channel, help_message)
        return
    elif message.content.lower().startswith(".pubg "):
        text = " ".join(message.content.split()).split()
        region = "na"
        game_type = "fpp"
        name = ""
        group = "solo,duo,squad"

        if len(text) < 2:
            yield from client.send_message(message.channel, "Please supply a username (e.g. !stats youda)")
            return
        else:
            name = text[1]
            for x in text[2:len(text)]:
                arg = x.lower()
                if arg in ["na", "as", "eu", "sea", "oc", "agg", "sa"]:
                    region = arg
                elif arg in ["fpp", "tpp"]:
                    game_type = arg
                elif arg in ["solo", "duo", "squad"]:
                    group = arg
                else:
                    errormsg = "Invalid argument `" + arg + "`\nAccepted values for region are (na, as, eu, sea, oc, sa, agg)\n"
                    errormsg +=  "Accepted values for game type are (fpp, tpp)\n"
                    errormsg +=  "Accepted values for group are (solo, duo, squad)"
                    yield from client.send_message(message.channel, errormsg)
                    return
        embed = yield from get_stats_embed(name, region, game_type, group)
        yield from client.send_message(message.channel, embed=embed)

client.run(DISCORD_TOKEN)
