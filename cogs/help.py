import discord
from discord.ext import commands
from dislash import slash_command, guild_only, has_role

class Help(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")

    @slash_command(description="Help for Flare")
    @guild_only()
    @has_role(935591008111042620)
    async def help(self, inter):
        embed = discord.Embed(
            title="Flare",
            colour=discord.Colour.purple()
        )
        embed.add_field(name="Play", value="Play a song", inline=False)
        embed.add_field(name="Join", value="Joins your current voice channel", inline=False)
        embed.add_field(name="Leave", value="Leaves the current voice channel", inline=False)
        embed.add_field(name="Search", value="Search for tracks by artist or song", inline=False)
        embed.add_field(name="Queue", value="Get the song queue", inline=False)
        embed.add_field(name="Pause", value="Pause the current song", inline=False)
        embed.add_field(name="Resume", value="Resume the current song", inline=False)
        embed.add_field(name="Skip", value="Skip the current song", inline=False)
        embed.add_field(name="Register [DM]", value="Register an account on Flare", inline=False)
        embed.add_field(name="Verify [DM]", value="Verify your account on Flare", inline=False)
        embed.add_field(name="Login [DM]", value="Login to your account on Flare", inline=False)
        embed.add_field(name="Upload [DM]", value="Upload a song to Flare", inline=False)
        embed.set_footer(text="Created by 0sir1s#0669 & astrid#0003")
        await inter.send(embed=embed)

def setup(bot):
    bot.add_cog(Help(bot))