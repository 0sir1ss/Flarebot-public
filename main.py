import discord
from discord.ext import commands
import json
import os
from dislash import InteractionClient, slash_command, Option, OptionType, is_owner
import dislash

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="%", intents=intents, case_insensitive=True, help_command=None)
client = InteractionClient(bot)
bot.config = json.loads(open('secrets.json').read())
bot.queue = {}
bot.authed_users = {}
bot.beta_users = []


@bot.event
async def on_ready():
    await bot.wait_until_ready()
    guild = bot.get_guild(878373535335194674)
    role = discord.utils.get(guild.roles, name='Beta Tester')
    for member in guild.members:
        if role in member.roles:
            bot.beta_users.append(member.id)
    print(f"-----\nReady to play // {bot.user.name} - {bot.user.id}\n-----")
    print(f'{len(bot.guilds)} servers\n-----')
    print(f'{len(bot.beta_users)} beta users\n-----')


@bot.event
async def on_slash_command_error(inter, error):
    if isinstance(error, dislash.application_commands.errors.MissingRole):
        embed = discord.Embed(
            title='Error',
            description='You are not a beta user',
            colour=discord.Colour.red()
        )
        return await inter.respond(embed=embed, ephemeral=True)
    if isinstance(error, dislash.application_commands.errors.PrivateMessageOnly):
        embed = discord.Embed(
            title='Error',
            description='This command can only be used in DMs',
            colour=discord.Colour.red()
        )
        return await inter.respond(embed=embed, ephemeral=True)
    if isinstance(error, dislash.application_commands.errors.NoPrivateMessage):
        embed = discord.Embed(
            title='Error',
            description='This command can only be used in Servers',
            colour=discord.Colour.red()
        )
        return await inter.respond(embed=embed, ephemeral=True)
    else:
        pass

@bot.event
async def on_command_error(ctx, error):
    pass

@slash_command(
    description="Add a user to beta", guild_ids=[878373535335194674], 
    options=[
        Option("user", "Enter the discord user", OptionType.USER, required=True)
    ]
)
@is_owner()
async def addbeta(inter, user):
    role = discord.utils.get(inter.guild.roles, name='Beta Tester')
    await user.add_roles(role)
    bot.beta_users.append(user.id)
    em = discord.Embed(
        title="Success",
        description=f"Gave {user.mention} Beta Access",
        colour=discord.Colour.green()
    )
    await inter.reply(embed=em)

@slash_command(
    name="load", 
    description="Load a cog", guild_ids=[935216658014945341], 
    options=[
        Option("name", "Enter the cog name", OptionType.STRING, required=True)
    ]
)
async def load(inter, name):
    try:
        bot.load_extension(f"cogs.{name}")
        em = discord.Embed(
            title="Success",
            description=f"Loaded extension **{name}.py**",
            colour=discord.Colour.green()
        )
        await inter.reply(embed=em)
    except Exception as e:
        em = discord.Embed(
            title="Error", 
            description=f"```py\n{e}\n```", 
            colour=discord.Colour.red()
            )
        await inter.reply(embed=em)

@slash_command(
    name="unload", 
    description="Unload a cog", guild_ids=[935216658014945341], 
    options=[
        Option("name", "Enter the cog name", OptionType.STRING, required=True)
    ]
)
async def unload(inter, name):
    try:
        bot.unload_extension(f"cogs.{name}")
        em = discord.Embed(
            title="Success",
            description=f"Unloaded extension **{name}.py**",
            colour=discord.Colour.green()
        )
        await inter.reply(embed=em)
    except Exception as e:
        em = discord.Embed(
            title="Error", 
            description=f"```py\n{e}\n```", 
            colour=discord.Colour.red()
            )
        await inter.reply(embed=em)

@slash_command(
    name="reload", 
    description="Reload a cog", guild_ids=[935216658014945341], 
    options=[
        Option("name", "Enter the cog name", OptionType.STRING, required=True)
    ]
)
async def reload(inter, name):
    try:
        bot.reload_extension(f"cogs.{name}")
        em = discord.Embed(
            title="Success",
            description=f"Reloaded extension **{name}.py**",
            colour=discord.Colour.green()
        )
        await inter.reply(embed=em)
    except Exception as e:
        em = discord.Embed(
            title="Error", 
            description=f"```py\n{e}\n```", 
            colour=discord.Colour.red()
            )
        await inter.reply(embed=em)

# Load the cogs in

for filename in os.listdir('./cogs'):
    if filename.endswith('.py') and not filename.startswith("_"):
        bot.load_extension(f'cogs.{filename[:-3]}')

bot.run(bot.config['token'], reconnect=True, bot=True)
