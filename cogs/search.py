import discord
from discord.ext import commands
from aiohttp import request
from util.buttons import Paginator as Pag
from dislash import slash_command, guild_only, Option, OptionType, has_role

class Search(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")

    @slash_command( 
        description="Search for tracks by artist or song", 
        options=[
            Option("artist", "Are you searching for an artist?", OptionType.BOOLEAN ,required=True),
            Option("query", "Enter your search query", OptionType.STRING ,required=True),
        ]
    )
    @guild_only()
    @has_role(935591008111042620)
    async def search(self, inter, artist, *, query):
        if artist == True:
            url = f'https://api.jointhe.vc/v1/tracks/search?artist={query}'
            async with request("GET", url, headers={}) as response:
                if response.status == 404:
                    embed = discord.Embed(
                        title='Error',
                        description=f'No results for artist: **{query}**',
                        colour=discord.Colour.red()
                    )
                    return await inter.respond(embed=embed)
                elif response.status == 200:
                    pages = []
                    n = 0

                    data = await response.json()
                    for track in data['tracks']:
                        name = track['name']
                        id = track['id']
                        artist = track['artist']
                        features = track['features']
                        if features != "":
                            pages.append(f'**Song**: {name}\n**Song ID**: `{id}`\n**Artist**: {artist} ft. {features}\n')
                        else:
                            pages.append(f'**Song**: {name}\n**Song ID**: `{id}`\n**Artist**: {artist}\n')
                        n += 1

                    await Pag(title=f"Search results for artist: {query}",
                            colour=discord.Colour.purple(),
                            entries=pages, length=5, footer=f'{n} results found', bot=self.bot).start(inter)
                else:
                    embed = discord.Embed(
                        title='Error',
                        description=f'We have received a {response.status} error',
                        colour=discord.Colour.red()
                    )
                    return await inter.respond(embed=embed)

        else:
            url = f'https://api.jointhe.vc/v1/tracks/search?name={query}'
            async with request("GET", url, headers={}) as response:
                if response.status == 404:
                    embed = discord.Embed(
                        title='Error',
                        description=f'No results for song name: **{query}**',
                        colour=discord.Colour.red()
                    )
                    return await inter.respond(embed=embed)
                elif response.status == 200:
                    pages = []
                    data = await response.json()
                    n = len(data['tracks'])

                    for track in data['tracks']:
                        name = track['name']
                        id = track['id']
                        artist = track['artist']
                        features = track['features']
                        if features != "":
                            pages.append(f'**Song:** {name}\n**Song ID:** `{id}`\n**Artist:** {artist} ft. {features}\n')
                        else:
                            pages.append(f'**Song:** {name}\n**Song ID:** `{id}`\n**Artist:** {artist}\n')

                    await Pag(title=f"Search results for song name: {query}",
                            colour=discord.Colour.purple(),
                            entries=pages, length=5, footer=f'{n} results found', bot=self.bot).start(inter)
                else:
                    embed = discord.Embed(
                        title='Error',
                        description=f'We have received a {response.status} error',
                        colour=discord.Colour.red()
                    )
                    return await inter.respond(embed=embed)

def setup(bot):
    bot.add_cog(Search(bot))
