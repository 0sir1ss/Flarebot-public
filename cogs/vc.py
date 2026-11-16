import discord
from discord.ext import commands
from discord.utils import get
from dislash import slash_command, guild_only, has_role

class VC(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")

    @slash_command( 
        description="Joins your current voice channel"
    )
    @guild_only()
    @has_role(935591008111042620)
    async def join(self, inter):
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
        else:
            await voice.move_to(vc)
        embed = discord.Embed(
            title='Success',
            description=f'I have connected to {vc.mention}',
            colour=discord.Colour.green()
        )
        await inter.respond(embed=embed)

    @slash_command( 
        description="Leaves the current voice channel"
    )
    @guild_only()
    @has_role(935591008111042620)
    async def leave(self, inter):
        vc = get(self.bot.voice_clients, guild=inter.guild)
        if vc is None:
            embed = discord.Embed(
                title='Error',
                description='I am not in a voice channel',
                colour=discord.Colour.red()
            )
            await inter.respond(embed=embed)

        else:
            embed = discord.Embed(
                title='Success',
                description=f'I have disconnected from {vc.channel.mention}',
                colour=discord.Colour.green()
            )
            await vc.disconnect()
            await inter.respond(embed=embed)
            self.bot.queue[inter.guild.id] = None

    @slash_command( 
        description="Pause the current song"
    )
    @guild_only()
    @has_role(935591008111042620)
    async def pause(self, inter):
        vc = get(self.bot.voice_clients, guild=inter.guild)
        if vc is None:
            embed = discord.Embed(
                title='Error',
                description='I am not in a voice channel',
                colour=discord.Colour.red()
            )
            await inter.respond(embed=embed)

        else:
            if vc.is_paused():
                embed = discord.Embed(
                    title='Error',
                    description='I am already paused\nPerhaps you were looking to **resume**',
                    colour=discord.Colour.red()
                )
                await inter.respond(embed=embed)
            else:
                embed = discord.Embed(
                    title='Success',
                    description=f'I have paused the music',
                    colour=discord.Colour.green()
                )
                vc.pause()
                await inter.respond(embed=embed)

    @slash_command( 
        description="Resume the current song"
    )
    @guild_only()
    @has_role(935591008111042620)
    async def resume(self, inter):
        vc = get(self.bot.voice_clients, guild=inter.guild)
        if vc is None:
            embed = discord.Embed(
                title='Error',
                description='I am not in a voice channel',
                colour=discord.Colour.red()
            )
            await inter.respond(embed=embed)

        else:
            if vc.is_paused():
                embed = discord.Embed(
                    title='Success',
                    description=f'I have resumed the music',
                    colour=discord.Colour.green()
                )
                vc.resume()
                await inter.respond(embed=embed)
            else:
                embed = discord.Embed(
                    title='Error',
                    description='I am already playing\nPerhaps you were looking to **pause**',
                    colour=discord.Colour.red()
                )
                await inter.respond(embed=embed)

def setup(bot):
    bot.add_cog(VC(bot))