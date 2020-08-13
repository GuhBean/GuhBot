# 3rd party modules
import discord
from discord.ext import commands
from apscheduler.triggers.cron import CronTrigger

# Builtin modules
from os import getcwd
from json import load, dump
from platform import python_version


class Meta(commands.Cog):

    """About the bot"""

    def __init__(self, client):
        self.client = client
        self._message = 'watching @GuhBot help | {guilds:,} servers & {users:,} users | version {version:s}'

        client.scheduler.add_job(self.set, CronTrigger(second=0))

    @property
    def message(self):
        """Status formatter"""

        return self._message.format(guilds=len(self.client.guilds), users=len(set(self.client.get_all_members())), version=self.client.version)

    @message.setter
    def message(self, value):
        """Message setter"""

        if value.split(' ')[0] not in ('playing', 'watching', 'listening-to', 'streaming'):
            raise ValueError('Invalid discord.Activity type.')
        self._message = value

    async def set(self):
        """Set the current bot status"""

        _type, _name = self.message.split(' ', maxsplit=1)
        await self.client.change_presence(activity=discord.Activity(
            name=_name,
            type=getattr(discord.ActivityType, _type, discord.ActivityType.watching),
        ))

    @commands.command(hidden=True)
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def help(self, ctx, *cog):
        """Displays this message"""

        if not cog:
            embed = discord.Embed(title='🔧Modules List',
                                  description=f"Do `{self.client.prefix(self.client, ctx.message)}help [module]` for more info on a specific module.",
                                  colour=ctx.author.colour,
                                  timestamp=ctx.message.created_at)

            cogs_desc = ''
            for x in self.client.cogs:
                if x.lower() == 'errors':
                    pass
                else:
                    cogs_desc += ('**{}** - {}'.format(x, self.client.cogs[x].__doc__)+'\n')
            embed.add_field(name='⚙️Modules', value=cogs_desc[0:len(cogs_desc)-1], inline=False)
            embed.set_author(name=f"{ctx.author.name}#{ctx.author.discriminator}",
                             icon_url=ctx.author.avatar_url)
            embed.set_thumbnail(url=self.client.user.avatar_url)
            await ctx.send(embed=embed)
        else:
            if len(cog) > 1:
                embed = discord.Embed(title='⛔Error!',
                                      description='That is way too many cogs!',
                                      colour=discord.Colour.red(),
                                      timestamp=ctx.message.created_at)
                embed.set_author(name=f"{ctx.author.name}#{ctx.author.discriminator}",
                                icon_url=ctx.author.avatar_url)
                embed.set_thumbnail(url=self.client.user.avatar_url)
                await ctx.send(embed=embed)
            else:
                found = False
                for x in self.client.cogs:
                    for y in cog:
                        if x.lower() == y.lower():
                            embed = discord.Embed(title='🚧Commands List',
                                                  description=f"List of GuhBot\'s Modular Commands.\nDo `{self.client.prefix(self.client, ctx.message)}help [command]` for more info on a command",
                                                  colour=ctx.author.colour,
                                                  timestamp=ctx.message.created_at)
                            scog_info = ''
                            for c in self.client.get_cog(y.capitalize()).get_commands():
                                if not c.hidden:
                                    scog_info += f"**{c.name}** - {c.help}\n"
                            embed.add_field(name=f"{cog[0].capitalize()} Module - {self.client.cogs[cog[0].capitalize()].__doc__}", value=scog_info)
                            embed.set_author(name=f"{ctx.author.name}#{ctx.author.discriminator}",
                                             icon_url=ctx.author.avatar_url)
                            embed.set_thumbnail(url=self.client.user.avatar_url)
                            found = True
                if not found:
                    for x in self.client.cogs:
                        for c in self.client.get_cog(x).get_commands():
                            if c.name == cog[0].lower():
                                embed = discord.Embed(title='🔧Command Syntax',
                                                      description='GuhBot\'s commands and how to use them.',
                                                      colour=ctx.author.colour,
                                                      timestamp=ctx.message.created_at)
                                embed.add_field(name=f"{c.name} - {c.help}",
                                                value=f"Proper Syntax:\n`{c.qualified_name} {c.signature}`",
                                                inline=False)
                                if c.aliases == [] or c.aliases == [None]:
                                    c.aliases.clear()
                                    c.aliases.append('No Aliases')
                                embed.add_field(name='Command Aliases',
                                                value=', '.join(c.aliases),
                                                inline=False)
                                embed.set_author(name=f"{ctx.author.name}#{ctx.author.discriminator}",
                                                 icon_url=ctx.author.avatar_url)
                                embed.set_thumbnail(url=self.client.user.avatar_url)
                        found = True
                else:
                    await ctx.message.add_reaction(emoji='👍')
                try:
                    await ctx.send(embed=embed)
                except UnboundLocalError:
                    embed = discord.Embed(title='⛔Error!',
                                          description=f"How would you even use the command or module \"{cog[0]}\"?\nSorry, but I don\'t see a command or module called \"{cog[0]}\"",
                                          colour=discord.Colour.red(),
                                          timestamp=ctx.message.created_at)
                    await ctx.send(embed=embed)

    @commands.command(aliases=['change_prefix'])
    @commands.cooldown(3, 10, commands.BucketType.guild)
    async def prefix(self, ctx, *, new_prefix='guh '):
        """Set a custom prefix for your server"""

        path = getcwd()+'/lib/config/prefixes.json'

        with open(path, 'r') as file:
            data = load(file)
        data[str(ctx.message.guild.id)] = new_prefix
        with open(path, 'w') as file:
            dump(data, file, indent=4)

        await ctx.send(f"Set the custom prefix to `{new_prefix}`\nDo `{new_prefix}prefix` to set it back to the default prefix.\nPing <@!624754986248831017> to check the current prefix.")

    @commands.command(aliases=['user_info', 'who_is'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def whois(self, ctx, member: discord.Member = None):
        """Get info on a specific user"""

        if not member:
            member = ctx.author

        roles = [role for role in member.roles]
        lenroles = len(roles)
        if lenroles == 1:
            mentions = f"@everyone"
            top_role = '@everyone'
            lenroles = lenroles
        else:
            mentions = " ".join([r.mention for r in member.roles if r != ctx.guild.default_role])
            top_role = member.top_role.mention
            lenroles = lenroles - 1
        if member == ctx.guild.owner:
            acknowledgements = 'Server Owner'
        elif member == self.client.user:
            acknowledgements = 'Hey that\'s me!'
        elif member.bot:
            acknowledgements = 'Discord Bot'
        elif member.guild_permissions.administrator:
            acknowledgements = 'Server Admin'
        else:
            acknowledgements = None

        embed = discord.Embed(description=f"{member.mention}\nID:{member.id}",
                              colour=member.colour,
                              timestamp=ctx.message.created_at)
        fields = [('Nickname', member.display_name, True),
                  ('Status', member.status, True),
                  ('Joined', member.joined_at.strftime('%a, %b %d, %Y, %I:%M %p'), False),
                  ('Registered', member.created_at.strftime('%a, %b %d, %Y, %I:%M %p'), True),
                  (f"Roles [{lenroles}]", mentions, False),
                  ('Highest Role', top_role, True)]
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)
        if acknowledgements:
            embed.add_field(name='Acknowledgements', value=acknowledgements)
        embed.set_thumbnail(url=member.avatar_url)
        embed.set_author(name=f"{member.name}#{member.discriminator}", icon_url=member.avatar_url)
        embed.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon_url)
        await ctx.send(embed=embed)

    @commands.command(aliases=['status', 'statistics', 'info', 'bot'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def stats(self, ctx):
        """Displays GuhBot's statistics"""

        botUsername = self.client.user.name
        websocketLatency = round(self.client.latency * 1000, 3)
        serverCount = len(self.client.guilds)
        memberCount = len(set(self.client.get_all_members()))
        botVersion = self.client.version
        pythonVer = python_version()
        dpyVer = discord.__version__

        embed = discord.Embed(title='Stats',
                              description=f"List of {botUsername}'s statistics",
                              colour=ctx.author.colour,
                              timestamp=ctx.message.created_at)
        fields = [('🏓 Pong', f"Websocket Latency: **{websocketLatency}ms**", True),
                  ('🔢 Server Count', f"Working in **{serverCount}** servers.", True),
                  ('👥 Member Count', f"Serving **{memberCount}** members.", True),
                  ('🌐 Version', f"GuhBot Version **{botVersion}**", True),
                  ('🐍 Python Version', f"{botUsername} runs on **Python {pythonVer}**.", True),
                  ('📜 Discord.py Version', f"{botUsername} runs on **Discord.py {dpyVer}**.", True),
                  ('🙋 Support Server', f"Join {self.client.user.name} [Support Server](https://discord.gg/gKvM8mE)", False)]
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)
        embed.set_footer(text=f"GuhBean#8433 | {botUsername}")
        embed.set_author(name=botUsername, icon_url=self.client.user.avatar_url)
        embed.set_thumbnail(url=self.client.user.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(aliases=['latency'])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def ping(self, ctx):
        """Returns the Discord API / Websocket latency"""

        websocketLatency = round(self.client.latency * 1000, 3)
        embed = discord.Embed(name='🏓 Pong',
                              description=f"Websocket Latency: **{websocketLatency}ms**",
                              colour=ctx.author.colour,
                              timestamp=ctx.message.created_at)
        embed.set_author(name=self.client.user.name, icon_url=self.client.user.avatar_url)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def support(self, ctx):
        """Returns both support server invite and the bot invite hyperlink"""

        embed = discord.Embed(title='Need Help❓',
                              description='Use the hyperlinks below to get access to the GuhBot support server',
                              colour=ctx.author.colour,
                              timestamp=ctx.message.created_at)
        embed.add_field(name='🙋 Support Server', value='[Server Link](https://discord.gg/gKvM8mE)')
        embed.add_field(name='🤖 Bot Invite',
                        value='[GuhBot invite](https://discord.com/api/oauth2/authorize?client_id=624754986248831017&permissions=536210679&scope=bot)')
        embed.set_author(name=self.client.user.name, icon_url=self.client.user.avatar_url)
        embed.set_thumbnail(url='https://media.giphy.com/media/9ZOyRdXL7ZVKg/giphy.gif')
        embed.set_footer(text='GuhBean#8433 | GuhBot')
        await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def upvote(self, ctx):
        """Support GuhBot? Upvote using this command!"""

        embed = discord.Embed(title='🔺Upvote GuhBot',
                              description='Provided hyperlinks bring you to GuhBot\'s upvote links.\nUpvoting the bot gets us more users 😀',
                              colour=ctx.author.colour,
                              timestamp=ctx.message.created_at)
        fields = [('Discord Bot List', '[discordbotlist.com](https://discordbotlist.com/bots/guhbot/upvote)', True),
                  ('Bots For Discord', '[botsfordiscord.com](https://botsfordiscord.com/bot/624754986248831017)', True)]
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)
        embed.set_author(name=self.client.user.name, icon_url=self.client.user.avatar_url)
        embed.set_thumbnail(url='https://media.giphy.com/media/4eQFLKTo1Tymc/giphy.gif')
        embed.set_footer(text='Thanks for upvoting GuhBot!👍')
        await ctx.send(embed=embed)

    @commands.command(aliases=['close', 'disconnect'], hidden=True)
    @commands.is_owner()
    async def logout(self, ctx):
        """This command disconnects the bot from all services."""

        await ctx.send(f":wave: Goodbye {ctx.author.mention}! I'm shutting dow...")
        await self.client.logout()
        print(f"{self.client.user.name} was logged out.")

    @logout.error
    async def logout_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            rickroll = 'https://media.giphy.com/media/lgcUUCXgC8mEo/giphy.gif'

            embed = discord.Embed(colour=ctx.author.colour,
                                  timestamp=ctx.message.created_at)
            embed.add_field(name='You Silly Billy 😜',
                            value=f"You thought you can actually use the logout command!")
            embed.set_image(url=rickroll)
            embed.set_author(name=f"{ctx.author.name}#{ctx.author.discriminator}",
                             icon_url=ctx.author.avatar_url)
            await ctx.send(embed=embed)
        else:
            raise error

    @commands.command(hidden=True)
    @commands.is_owner()
    async def load(self, ctx, *, cog):
        """Cog loader"""

        self.client.load_extension(f"lib.cogs.{cog}")
        await ctx.send(f"`{cog} loaded successfully.`")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def unload(self, ctx, *, cog):
        """Cog unloader"""

        self.client.unload_extension(f"lib.cogs.{cog}")
        await ctx.send(f"`{cog} unloaded successfully.`")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def reload(self, ctx, *, cog):
        """Cog reloader. Unload then reload"""

        self.client.unload_extension(f"lib.cogs.{cog}")
        self.client.load_extension(f"lib.cogs.{cog}")
        await ctx.send(f"`{cog} reloaded successfully.`")

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.client.ready:
            self.client.cogs_ready.ready_up('Meta')

def setup(client):
    client.add_cog(Meta(client))
