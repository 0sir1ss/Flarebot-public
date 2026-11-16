from aiohttp import request
import discord
from discord.ext import commands
from dislash import slash_command, dm_only, Option, OptionType, ActionRow, Button, ButtonStyle, check
import requests
import asyncio

class Account(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
    

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")

    @slash_command(
        description="Register an account on Flare",
        options=[
            Option("username", "Enter your username for Flare", OptionType.STRING ,required=True),
            Option("password", "Enter your password for Flare", OptionType.STRING ,required=True),
            Option("email", "Enter your email for Flare", OptionType.STRING ,required=True)
        ]
    )
    @dm_only()
    async def register(self, inter, username, password, email):
        if inter.author.id not in self.bot.beta_users:
            embed = discord.Embed(
                title='Error',
                description='You are not a beta user',
                colour=discord.Colour.red()
            )
            return await inter.respond(embed=embed, ephemeral=True)
        payload = {
            "username": username,
            "password": password,
            "email": email
        }
        url = "https://api.jointhe.vc/v1/account/create"
        async with request("POST", url, headers={'Content-Type': 'application/json'}, json=payload) as response:
            if response.status == 400:
                data = await response.json()
                embed = discord.Embed(
                    title='Error',
                    description=data['err'],
                    colour=discord.Colour.red()
                )
                return await inter.respond(embed=embed, ephemeral=True)
            elif response.status == 200:
                embed = discord.Embed(
                    title='Success',
                    description='Successfully registered your account\nPlease run `/verify` with the code in your email.\nIf you need to get another code run `/reverify`', 
                    colour=discord.Colour.green()
                )
                return await inter.respond(embed=embed, ephemeral=True)
            else:
                embed = discord.Embed(
                    title='Error',
                    description=f'We have received a {response.status} error',
                    colour=discord.Colour.red()
                )
                return await inter.respond(embed=embed, ephemeral=True)

    @slash_command(
        description="Verify your account on Flare",
        options=[
            Option("username", "Enter your username for Flare", OptionType.STRING ,required=True),
            Option("code", "Enter your verification code for Flare", OptionType.STRING ,required=True)
        ]
    )
    @dm_only()
    async def verify(self, inter, username, code):
        if inter.author.id not in self.bot.beta_users:
            embed = discord.Embed(
                title='Error',
                description='You are not a beta user',
                colour=discord.Colour.red()
            )
            return await inter.respond(embed=embed, ephemeral=True)
        payload = {
            "username": username,
            "verificationCode": code
        }
        url = "https://api.jointhe.vc/v1/account/verify"
        async with request("POST", url, headers={'Content-Type': 'application/json'}, json=payload) as response:
            if response.status == 400:
                data = await response.json()
                embed = discord.Embed(
                    title='Error',
                    description=data['err'],
                    colour=discord.Colour.red()
                )
                return await inter.respond(embed=embed, ephemeral=True)
            elif response.status == 404:
                data = await response.json()
                embed = discord.Embed(
                    title='Error',
                    description=data['err'],
                    colour=discord.Colour.red()
                )
                return await inter.respond(embed=embed, ephemeral=True)
            elif response.status == 201:
                embed = discord.Embed(
                    title='Success',
                    description='Successfully verified and your account\nRun `/login` to login to your account', 
                    colour=discord.Colour.green()
                )
                return await inter.respond(embed=embed, ephemeral=True)
            else:
                embed = discord.Embed(
                    title='Error',
                    description=f'We have received a {response.status} error',
                    colour=discord.Colour.red()
                )
                return await inter.respond(embed=embed, ephemeral=True)

    @slash_command(
        description="Login to your account on Flare",
        options=[
            Option("username", "Enter your username/email for Flare", OptionType.STRING ,required=True),
            Option("password", "Enter your password for Flare", OptionType.STRING ,required=True)
        ]
    )
    @dm_only()
    async def login(self, inter, username, password):
        if inter.author.id not in self.bot.beta_users:
            embed = discord.Embed(
                title='Error',
                description='You are not a beta user',
                colour=discord.Colour.red()
            )
            return await inter.respond(embed=embed, ephemeral=True)
        if inter.author.id in self.bot.authed_users:
            embed = discord.Embed(
                title='Error',
                description='You are already logged in',
                colour=discord.Colour.red()
            )
            return await inter.respond(embed=embed, ephemeral=True)
        if '@' in username:
            payload = {
                "email": username,
                "password": password
            }
        else:
            payload = {
                "username": username,
                "password": password
            }
        url = "https://api.jointhe.vc/v1/account/login"
        async with request("POST", url, headers={'Content-Type': 'application/json'}, json=payload) as response:
            if response.status == 404 or response.status == 401:
                data = await response.json()
                embed = discord.Embed(
                    title='Error',
                    description=data['err'],
                    colour=discord.Colour.red()
                )
                return await inter.respond(embed=embed, ephemeral=True)
            elif response.status == 200:
                data = await response.json()
                self.bot.authed_users[inter.author.id] = data['accessToken']
                embed = discord.Embed(
                    title='Success',
                    description='Successfully logged into your account\nYou will be logged out after 5 minutes', 
                    colour=discord.Colour.green()
                )
                await inter.respond(embed=embed, ephemeral=True)
                await asyncio.sleep(300)
                self.bot.authed_users.pop(inter.author.id)
            else:
                embed = discord.Embed(
                    title='Error',
                    description=f'We have received a {response.status} error',
                    colour=discord.Colour.red()
                )
                return await inter.respond(embed=embed, ephemeral=True)

    @slash_command(
        description="Upload a song to Flare", 
        options=[
            Option("name", "Enter the song name", OptionType.STRING ,required=True),
            Option("artist", "Enter the song artist", OptionType.STRING ,required=True),
            Option("features", "Enter the names for feature in the song", OptionType.STRING)
        ]
    )
    @dm_only()
    async def upload(self, inter, name, artist, features=None):
        if inter.author.id not in self.bot.beta_users:
            embed = discord.Embed(
                title='Error',
                description='You are not a beta user',
                colour=discord.Colour.red()
            )
            return await inter.respond(embed=embed, ephemeral=True)
        if inter.author.id not in self.bot.authed_users:
            embed = discord.Embed(
                title='Error',
                description='You are not logged in',
                colour=discord.Colour.red()
            )
            return await inter.respond(embed=embed, ephemeral=True)

        def check(m):
            return m.author.id == inter.author.id and m.channel.id == inter.channel.id
        if features:
            embed = discord.Embed(
                title="Confirmation", colour=discord.Colour.purple(), 
                description=f"**Name:** {name}\n**Artist:** {artist}\n**Features:** {features}"
            )
        else:
            embed = discord.Embed(
                title="Confirmation", colour=discord.Colour.purple(), 
                description=f"**Name:** {name}\n**Artist:** {artist}"
            )
        row = ActionRow(
            Button(
                style=ButtonStyle.green,
                label="Confirm",
                custom_id="yes"
            ),
            Button(
                style=ButtonStyle.red,
                label="Cancel",
                custom_id="no"
            )
        )
        msg = await inter.reply(embed=embed, components=[row], ephemeral=True)
        def check(m):
            return inter.author.id == m.author.id
        try:
            inter = await msg.wait_for_button_click(check=check, timeout=60.0)
        except asyncio.TimeoutError:
            embed = discord.Embed(
                title="Cancelled",
                description="You took too long to confirm\nPlease try again",
                colour=discord.Colour.red()
            )
            return await inter.respond(embed=embed, ephemeral=True)
        button = inter.clicked_button.custom_id
        if button == "no":
            embed = discord.Embed(
                title="Cancelled",
                description="You have cancelled the upload process",
                colour=discord.Colour.red()
            )
            return await inter.respond(embed=embed, ephemeral=True)
        else:
            embed = discord.Embed(
                title="File Upload", colour=discord.Colour.purple(), 
                description="Please send the .mp3 file you wish to upload"
            )
            await inter.respond(embed=embed, ephemeral=True)
            try:
                msg = await self.bot.wait_for('message', check=check, timeout=60.0)
            except asyncio.TimeoutError:
                embed = discord.Embed(
                    title="Cancelled",
                    description="You took too long to send your file\nPlease try again",
                    colour=discord.Colour.red()
                )
                return await inter.respond(embed=embed, ephemeral=True)
            url = msg.attachments[0].url
            if not url.endswith('.mp3'):
                embed = discord.Embed(
                    title="Cancelled",
                    description="Please send a .mp3",
                    colour=discord.Colour.red()
                )
                return await inter.followup(embed=embed, ephemeral=True)
            song = requests.get(url).content

            url = "https://api.jointhe.vc/v1/tracks/upload"
            payload = {
                "trackName": name,
                "artist": artist,
                "features": features or '',
                "file": song
            }
            async with request("POST", url, data=payload, headers={'Authorization': self.bot.authed_users[inter.author.id]}) as response:
                if response.status == 400 or response.status == 401:
                    data = await response.json()
                    embed = discord.Embed(
                        title='Error',
                        description=data['err'],
                        colour=discord.Colour.red()
                    )
                    return await inter.followup(embed=embed, ephemeral=True)
                if response.status == 201:
                    data = await response.json()
                    embed = discord.Embed(
                        title='Success',
                        description=f'Successfully uploaded your song\n**Track ID:** {data["trackId"]}', 
                        colour=discord.Colour.green()
                    )
                    return await inter.followup(embed=embed, ephemeral=True)
                else:
                    embed = discord.Embed(
                        title='Error',
                        description=f'We have received a {response.status} error',
                        colour=discord.Colour.red()
                    )
                    return await inter.followup(embed=embed, ephemeral=True)

def setup(bot):
    bot.add_cog(Account(bot))