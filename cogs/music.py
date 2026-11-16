import discord
from discord.utils import get
from discord.ext import commands
from aiohttp import request
from util.buttons import Paginator as Pag
from dislash import slash_command, guild_only, Option, OptionType, has_role
class Music(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.FFMPEG_OPTIONS = {
            'before_options': f'-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 ',
            'options': '-vn'
        }

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")

    def playNext(self, inter):
        """
        Remove the first song within the queue and then play the next one.
        Use the `after` parameter to be recursive.
        Handles empty queues.
        """
        try:
            if self.bot.queue[inter.guild.id] == []:
                self.bot.queue[inter.guild.id] = None
            else:
                self.bot.queue[inter.guild.id].pop(0)
                vc = get(self.bot.voice_clients, guild=inter.guild)
                song = self.bot.queue[inter.guild.id][0][0]
                vc.play(discord.FFmpegPCMAudio(f'https://cdn.jointhe.vc/v1/files/{song}', **self.FFMPEG_OPTIONS), after=lambda e: self.playNext(inter))

        except (IndexError, AttributeError, KeyError):
            if self.bot.queue[inter.guild.id] == []:
                self.bot.queue[inter.guild.id] = None
            else:
                self.bot.queue[inter.guild.id].pop(0)


    @slash_command( 
        description="Play a song", 
        options=[
            Option("songid", "Enter the Song ID", OptionType.STRING ,required=True),
        ]
    )
    @guild_only()
    @has_role(935591008111042620)
    async def play(self, inter, songid):
        if inter.author.voice is None:
            embed = discord.Embed(
                title='Error',
                description='You are not in a voice channel',
                colour=discord.Colour.red()
            )
            return await inter.respond(embed=embed)
        
        vc = inter.author.voice.channel
        voice = get(self.bot.voice_clients, guild=inter.guild)
        if voice is None:
            await vc.connect()
            embed = discord.Embed(
                title='Success',
                description=f'I have connected to {vc.mention}',
                colour=discord.Colour.green()
            )
            await inter.respond(embed=embed)
            rejoined = True
        else:
            if voice.channel.id == vc.id:
                rejoined = False
            else:
                await voice.move_to(vc)
                embed = discord.Embed(
                    title='Success',
                    description=f'I have connected to {vc.mention}',
                    colour=discord.Colour.green()
                )
                await inter.respond(embed=embed)
                rejoined = True


        url = f'https://api.jointhe.vc/v1/tracks/info/{songid}'
        async with request("GET", url, headers={}) as response:
            if response.status == 200:
                data = await response.json()
                name = data['name']
                artist = data['artist']
                features = data['features']
                song = data['cdnURL']
                uploader = data['uploader']['username']
                uploaderBadges = data['uploader']['badges']
                tracks = data['uploader']['tracks']
                badge = uploaderBadges[len(uploaderBadges) - 1]

            elif response.status == 404:
                embed = discord.Embed(
                    title='Error',
                    description=f'There is no song with the following song ID: `{songid}`',
                    colour=discord.Colour.red()
                )
                if rejoined:
                    return await inter.followup(embed=embed)
                else:
                    return await inter.respond(embed=embed)
            
            else:
                embed = discord.Embed(
                    title='Error',
                    description=f'We have received a {response.status} error',
                    colour=discord.Colour.red()
                )
                if rejoined:
                    return await inter.followup(embed=embed)
                else:
                    return await inter.respond(embed=embed)


        src = discord.FFmpegPCMAudio(song, **self.FFMPEG_OPTIONS)
        vc = get(self.bot.voice_clients, guild=inter.guild)
        try:
            self.bot.queue[inter.guild.id].append([songid, f'{inter.author.name}#{inter.author.discriminator}'])
            if features != "":
                desc = f'Added **{name}** from **{artist}** ft. **{features}** to the queue'
            else:
                desc = f'Added **{name}** from **{artist}** to the queue'
            uploaderinfo = f"\n[{badge}] {uploader} - {tracks} {'tracks' if tracks > 1 else 'track'}"
            embed = discord.Embed(
                title='Success',
                description=desc,
                colour=discord.Colour.green()
            )
            embed.add_field(name="Uploader", value=uploaderinfo, inline=False)
            embed.set_footer(text=f'Song ID: {songid}')
            if rejoined:
                return await inter.followup(embed=embed)
            else:
                return await inter.respond(embed=embed)
        except:
            self.bot.queue[inter.guild.id] = [[songid, f'{inter.author.name}#{inter.author.discriminator}']]
            try:
                vc.play(src, after=lambda e: self.playNext(inter)) # Recursively play next song
                if features != "":
                    desc = f'Now playing **{name}** from **{artist}** ft. **{features}**'
                else:
                    desc = f'Now playing **{name}** from **{artist}**'
                uploaderinfo = f"\n[{badge}] {uploader} - {tracks} {'tracks' if tracks > 1 else 'track'}"
                embed = discord.Embed(
                    title='Success',
                    description=desc,
                    colour=discord.Colour.green()
                )
                embed.add_field(name="Uploader", value=uploaderinfo, inline=False)
                embed.set_footer(text=f'Song ID: {songid}')
                if rejoined:
                    return await inter.followup(embed=embed)
                else:
                    return await inter.respond(embed=embed)
            except:
                embed = discord.Embed(
                    title='Error',
                    description=f'An unknown error has occurred whilst trying to play song: `{songid}`',
                    colour=discord.Colour.red()
                )
                if rejoined:
                    return await inter.followup(embed=embed)
                else:
                    return await inter.respond(embed=embed)


    @slash_command( 
        description="Skip the current song"
    )
    @guild_only()
    @has_role(935591008111042620)
    async def skip(self, inter):
        if inter.author.voice is None:
            embed = discord.Embed(
                title='Error',
                description='You are not in a voice channel',
                colour=discord.Colour.red()
            )
            return await inter.respond(embed=embed)
        vc = get(self.bot.voice_clients, guild=inter.guild)
        if vc is None:
            embed = discord.Embed(
                title='Error',
                description='I am not in a voice channel',
                colour=discord.Colour.red()
            )
            return await inter.respond(embed=embed)
        try:
            if self.bot.queue[inter.guild.id] is None or self.bot.queue[inter.guild.id] == []:
                embed = discord.Embed(
                    title='Error',
                    description='There are currently no queued songs',
                    colour=discord.Colour.red()
                )
                return await inter.respond(embed=embed)
        except:
                embed = discord.Embed(
                    title='Error',
                    description='There are currently no queued songs',
                    colour=discord.Colour.red()
                )
                return await inter.respond(embed=embed)

        vc = get(self.bot.voice_clients, guild=inter.guild)
        vc.pause()
        if self.bot.queue[inter.guild.id] != None or self.bot.queue[inter.guild.id] != []:
            if len(self.bot.queue[inter.guild.id]) > 1:
                song = self.bot.queue[inter.guild.id][1][0]
            else:
                song = self.bot.queue[inter.guild.id][0][0]
            vc.play(discord.FFmpegPCMAudio(f'https://cdn.jointhe.vc/v1/files/{song}', **self.FFMPEG_OPTIONS), after=lambda e: self.playNext(inter))

        embed = discord.Embed(
            title='Success',
            description='Successfully skipped the song',
            colour=discord.Colour.green()
        )
        await inter.respond(embed=embed)



    @slash_command( 
        description="Get the song queue"
    )
    @guild_only()
    @has_role(935591008111042620)
    async def queue(self, inter):
        try:
            if self.bot.queue[inter.guild.id] is None or self.bot.queue[inter.guild.id] == []:
                embed = discord.Embed(
                    title='Error',
                    description='There are currently no queued songs',
                    colour=discord.Colour.red()
                )
                return await inter.respond(embed=embed)
        except:
                embed = discord.Embed(
                    title='Error',
                    description='There are currently no queued songs',
                    colour=discord.Colour.red()
                )
                return await inter.respond(embed=embed)
        pages = []
        for song in self.bot.queue[inter.guild.id]:
            songid = song[0]
            added = song[1]
            url = f'https://api.jointhe.vc/v1/tracks/info/{songid}'
            async with request("GET", url, headers={}) as response:
                if response.status == 200:
                    data = await response.json()
                    name = data['name']
                    artist = data['artist']
                    features = data['features']
                else:
                    embed = discord.Embed(
                        title='Error',
                        description=f'We have received a {response.status} error',
                        colour=discord.Colour.red()
                    )
                    return await inter.respond(embed=embed)

            if features != "":
                pages.append(f'**Song:** {name}\n**Song ID:** {songid}\n**Artist:** {artist} ft. {features}\n**Added By:** {added}\n')
            else:
                pages.append(f'**Song:** {name}\n**Song ID:** {songid}\n**Artist:** {artist}\n**Added By:** {added}\n')

        await Pag(title=f"Queue in {inter.guild.name}",
                colour=discord.Colour.purple(),
                entries=pages, length=5, footer=f'{len(self.bot.queue[inter.guild.id])} tracks queued', bot=self.bot).start(inter)

def setup(bot):
    bot.add_cog(Music(bot))