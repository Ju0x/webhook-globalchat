import discord
from discord import Webhook, AsyncWebhookAdapter
from discord.ext import commands
from datetime import datetime
import json
import aiohttp

red = 0xFF4A4A
green = 0x67D676

with open("settings.json") as file:
    settings = json.load(file)

extensions = [
    "extensions.commands"
]

last_message = {}
warned = {}


class Main(commands.Bot):

    async def on_ready(self):
        print("> Bot started successfully!")

    def global_check(self, message, servers):

        try:
            if message.channel.id == servers[str(message.guild.id)]["channel"]:
                return True
        except:
            return False

    async def get_webhook_url(self, message, server, servers):

        channel = bot.get_channel(servers[server]["channel"])
        webhooks = await channel.webhooks()

        for i in webhooks:
            if i.id == servers[server]["webhook"]:
                return i.url

    async def send_webhook(self, message, server: str, servers):

        async with aiohttp.ClientSession() as session:

            url = await self.get_webhook_url(message, server, servers)

            if url is None:
                return

            webhook = Webhook.from_url(
                url,
                adapter=AsyncWebhookAdapter(session)
            )

            user = str(message.author)
            avatar = str(message.author.avatar_url)
            content = message.content

            if message.attachments:
                content = f"{message.content}\n{message.attachments[0].url}"

            await webhook.send(
                content,
                username=user,
                avatar_url=avatar
            )

    async def on_message(self, message):

        with open("global_servers.json") as file:
            servers = json.load(file)

        if message.author.bot:
            return

        if self.global_check(message, servers):

            if message.author.id not in settings["automod_ignored_ids"]:

                # +++++ Automod checks +++++

                # Anti-invite

                payload = message.content.lower().replace(" ", "").replace(".", "").replace("\n", "").replace("/", "")

                invites = [
                    "discordgg", "invitegg", "discordio", "discordlink", "discordme", "discordplus", "disboardorg"
                ]

                violation = None

                for invite in invites:

                    if invite in payload:
                        violation = "Invite-Link"

                # Anti-ping

                if "@everyone" in message.content or "@here" in message.content:
                    violation = "everyone/here ping"

                mention_count = 0
                for i in message.mentions:
                    mention_count = mention_count + 1

                if mention_count > 3:
                    violation = "massping"

                # Anti-link

                link = True
                whitelist = settings["link_whitelist"]
                args = message.content.split(" ")
                if len(message.content) > 9:
                    for arg in args:

                        if "https://" in arg or "http://" in arg:

                            parsed_link = arg.split("/")

                            for link_fragment in parsed_link:

                                if link_fragment in whitelist:
                                    link = False
                        else:
                            link = False
                else:
                    link = False

                if link:
                    violation = "link"

                # Anti-Badword

                with open("badwords.json") as file:
                    badwords = json.load(file)

                for word in badwords["badwords"]:
                    if word in message.content.lower():
                        violation = "badwords"

                # Warn

                if violation is not None:
                    await message.delete()

                    embed = discord.Embed(
                        description=f"**Reason:** `{violation}`",
                        color=red,
                        timestamp=datetime.utcnow()
                    ).set_author(
                        name="Your message has been blocked!",
                        icon_url=message.author.avatar_url
                    ).set_footer(
                        text=f"{message.author} | {message.author.id}"
                    )

                    await message.channel.send(embed=embed)
                    return

                # Antispam

                try:

                    cooldown = settings["antispam_cooldown"]
                    last_message_time = (datetime.now() - last_message[str(message.author.id)]).seconds

                    if last_message_time <= cooldown:
                        embed = discord.Embed(
                            color=red,
                            timestamp=datetime.utcnow()
                        ).set_author(
                            name=f"{message.author.name}, the globalchat is on cooldown! Please wait a few seconds!",
                            icon_url=message.author.avatar_url
                        ).set_footer(
                            text="Warning"
                        )

                        await message.channel.send(embed=embed)

                        return

                except:
                    pass

                last_message[str(message.author.id)] = datetime.now()

            # +++++ Send message to all guilds +++++

            await message.add_reaction("✅")

            for server in servers:
                if not int(server) == message.guild.id:
                    await self.send_webhook(message, server, servers)

        await bot.process_commands(message)

    async def on_command_error(self, ctx, err):

        print(err)

        if not isinstance(err, commands.CommandNotFound):

            desc = "**An error occurred!**\n" \
                   "Please check, if you used the command correctly!"

            if isinstance(err, commands.CommandOnCooldown):
                desc = "**Please wait. This command is on cooldown!**"

            if isinstance(err, commands.MissingPermissions):
                desc = "**You don't have permissions to execute this command!**"

            if isinstance(err, commands.BotMissingPermissions) or "Forbidden" in str(err):
                desc = "**I don't have enough permissions to execute the command!**"

            embed = discord.Embed(
                description=desc,
                color=red
            )

            await ctx.send(embed=embed)


prefix = settings["prefix"]
case_insensitive = settings["case_insensitive"]
intents = discord.Intents.all()
token = settings["token"]

bot = Main(command_prefix=prefix, intents=intents, case_insensitive=case_insensitive)

bot.remove_command("help") # To disable the discord.py help command.

if __name__ == "__main__":

    for i in extensions:
        bot.load_extension(i)

bot.run(token)
