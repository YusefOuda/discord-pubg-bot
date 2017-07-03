import discord
import asyncio
import requests
import datetime
from keys import TRN_API_KEY, DISCORD_API_KEY

client = discord.Client()

def get_stats_embed(username):
    print(username)
    headers = {'TRN-Api-Key': TRN_API_KEY}
    r = requests.get('https://pubgtracker.com/api/profile/pc/' + username, headers=headers)
    if r.status_code != 200:
        embed = discord.Embed(title="Could not get stats for player " + username, colour=discord.Colour(0xe74c3c))
        return embed
    json = r.json()
    embed = discord.Embed(title="Full Stats", colour=discord.Colour(0x316a7b), url="https://pubgtracker.com/profile/pc/" + username, timestamp=datetime.datetime.utcnow())
    embed.set_footer(text="Bot created by Yusef Ouda", icon_url="https://cdn.discordapp.com/embed/avatars/0.png")
    embed.set_thumbnail(url=json['Avatar'])
    embed.set_author(name=username, url="https://pubgtracker.com/profile/pc/" + username, icon_url=json['Avatar'])
    embed.add_field(name=":walking: __Solo__ :walking:", value="Wins: " + get_stat(json['Stats'], 'solo', 'Wins') + ' - Rank: ' + str(get_stat(json['Stats'], 'solo', 'Rating', 'rank')), inline=False)
    embed.add_field(name="Rating", value=get_stat(json['Stats'], 'solo', 'Rating'), inline=True)
    embed.add_field(name="Win Percentage", value=get_stat(json['Stats'], 'solo', 'WinRatio'), inline=True)
    embed.add_field(name="Top 10 Percentage", value=get_stat(json['Stats'], 'solo', 'Top10Ratio'), inline=True)
    embed.add_field(name="K/D Ratio", value=get_stat(json['Stats'], 'solo', 'KillDeathRatio'), inline=True)
    embed.add_field(name="Total Kills", value=get_stat(json['Stats'], 'solo', 'Kills'), inline=True)
    embed.add_field(name="Most Kills", value=get_stat(json['Stats'], 'solo', 'RoundMostKills'), inline=True)
    embed.add_field(name=":couple: __Duo__ :couple:", value="Wins: " + get_stat(json['Stats'], 'duo', 'Wins') + ' - Rank: ' + str(get_stat(json['Stats'], 'duo', 'Rating', 'rank')), inline=False)
    embed.add_field(name="Rating", value=get_stat(json['Stats'], 'duo', 'Rating'), inline=True)
    embed.add_field(name="Win Percentage", value=get_stat(json['Stats'], 'duo', 'WinRatio'), inline=True)
    embed.add_field(name="Top 10 Percentage", value=get_stat(json['Stats'], 'duo', 'Top10Ratio'), inline=True)
    embed.add_field(name="K/D Ratio", value=get_stat(json['Stats'], 'duo', 'KillDeathRatio'), inline=True)
    embed.add_field(name="Total Kills", value=get_stat(json['Stats'], 'duo', 'Kills'), inline=True)
    embed.add_field(name="Most Kills", value=get_stat(json['Stats'], 'duo', 'RoundMostKills'), inline=True)
    embed.add_field(name=":family: __Squad__ :family:", value="Wins: " + get_stat(json['Stats'], 'squad', 'Wins') + ' - Rank: ' + str(get_stat(json['Stats'], 'squad', 'Rating', 'rank')), inline=False)
    embed.add_field(name="Rating", value=get_stat(json['Stats'], 'squad', 'Rating'), inline=True)
    embed.add_field(name="Win Percentage", value=get_stat(json['Stats'], 'squad', 'WinRatio'), inline=True)
    embed.add_field(name="Top 10 Percentage", value=get_stat(json['Stats'], 'squad', 'Top10Ratio'), inline=True)
    embed.add_field(name="K/D Ratio", value=get_stat(json['Stats'], 'squad', 'KillDeathRatio'), inline=True)
    embed.add_field(name="Total Kills", value=get_stat(json['Stats'], 'squad', 'Kills'), inline=True)
    embed.add_field(name="Most Kills", value=get_stat(json['Stats'], 'squad', 'RoundMostKills'), inline=True)
    return embed

def get_stat(stats, group, field, default="displayValue"):
    for grp in stats:
        if grp['Match'] == group:
            for stat in grp['Stats']:
                if stat['field'] == field:
                    return stat[default]
    
@client.event
@asyncio.coroutine
def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

@client.event
@asyncio.coroutine
def on_message(message):
    if message.content.startswith('!stats'):
        text = message.content.split(' ')
        if len(text) < 2:
            yield from client.send_message(message.channel, 'Please supply a username (e.g. !stats youda)')
        yield from client.send_message(message.channel, embed=get_stats_embed(text[1]))

client.run(DISCORD_API_KEY)
