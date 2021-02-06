import discord
from discord.ext import commands
import json
from datetime import datetime

red = 0xFF4A4A
green = 0x67D676
servers = "global_servers.json"

class Commands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def send_info(self, ctx, info: str):

        embed = discord.Embed(
            title="Error!",
            description=info,
            color=red,
            timestamp=datetime.utcnow()
        ).set_footer(
            text=ctx.guild.name
        )

        await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(3, 10, commands.BucketType.guild)
    async def help(self, ctx):

        embed = discord.Embed(
            description="**Help | Globalchat**",
            color=green,
            timestamp=datetime.utcnow()
        ).add_field(
            name="help",
            value="`Shows this message`",
            inline=False
        ).add_field(
            name="setglobal #channel",
            value="```\nSets the Global in a specific channel```"
        ).add_field(
            name="removeglobal",
            value="```\nRemoves the Global from the Server```"
        ).add_field(
            name="⚡ Owner-Commands",
            value="That are commands only the Bot-Owner can execute",
            inline=False
        ).add_field(
            name="addword <word>",
            value="```\nAdds a word to the badword-list```"
        ).add_field(
            name="removeword <word>",
            value="```\nRemoves a word from the badword-list```"
        ).add_field(
            name="> Credits:",
            value="WebHook Global made by Juox#0001",
            inline=False
        ).set_thumbnail(
            url=ctx.guild.icon_url
        )

        await ctx.send(embed=embed)

    @commands.command(aliases=["sg", "addglobal", "setchannel", "addchannel"])
    @commands.cooldown(2, 10, commands.BucketType.guild)
    @commands.has_guild_permissions(administrator=True)
    async def setglobal(self, ctx, channel: discord.TextChannel = None):

        if ctx.author.bot:
            return

        if channel is None:
            await self.send_info(ctx, "please provide a channel")
            return

        with open(servers, "r") as file:
            data = json.load(file)

        try:
            if channel.id == data[str(ctx.guild.id)]:
                await self.send_info(ctx, "This channel is already set as global!")
                return
        except:
            pass

        w = await channel.create_webhook(name="Globalchat")

        data[str(ctx.guild.id)] = {}
        data[str(ctx.guild.id)]["channel"] = channel.id
        data[str(ctx.guild.id)]["webhook"] = w.id

        with open(servers, "w+") as file:
            json.dump(data, file, indent=4)

        embed = discord.Embed(
            color=green,
            timestamp=datetime.utcnow()
        ).set_footer(
            text="Globalchat"
        ).set_author(
            name=f"Globalchat was set successfully in {channel.name}!",
            icon_url=ctx.author.avatar_url
        )

        await ctx.send(embed=embed)

    @commands.command(aliases=["rg", "deleteglobal", "removechannel"])
    @commands.cooldown(2, 10, commands.BucketType.guild)
    @commands.has_guild_permissions(administrator=True)
    async def removeglobal(self, ctx):

        if ctx.author.bot:
            return

        with open(servers, "r") as file:
            data = json.load(file)

        channel = self.bot.get_channel(data[str(ctx.guild.id)]["channel"])
        webhook = await channel.webhooks()
        for i in webhook:
            if i.id == data[str(ctx.guild.id)]["webhook"]:
                await i.delete()

        data.pop(str(ctx.guild.id))

        with open(servers, "w+") as file:
            json.dump(data, file, indent=4)

        embed = discord.Embed(
            color=green,
            timestamp=datetime.utcnow()
        ).set_footer(
            text="Globalchat"
        ).set_author(
            name=f"Globalchat has been removed!",
            icon_url=ctx.author.avatar_url
        )

        await ctx.send(embed=embed)

    @commands.command()
    @commands.is_owner()
    async def addword(self, ctx, word: str):

        with open("badwords.json", encoding="utf-8") as file:
            words = json.load(file)

        if word.lower() in words["badwords"]:
            await self.send_info(ctx, "This word is already in the list!")
            return

        word = word.lower()
        words["badwords"].append(word)

        with open("badwords.json", "w+", encoding="utf-8") as file:
            json.dump(words, file, indent=4)

        await ctx.send("Word has been added!")

    @commands.command()
    @commands.is_owner()
    async def removeword(self, ctx, word: str):

        with open("badwords.json", encoding="utf-8") as file:
            words = json.load(file)

        if not word.lower() in words["badwords"]:
            await self.send_info(ctx, "This word is not in the list!")
            return
        word = word.lower()
        words["badwords"].remove(word)

        with open("badwords.json", "w+", encoding="utf-8") as file:
            json.dump(words, file, indent=4)

        await ctx.send("Word has been removed!")

def setup(bot):
    bot.add_cog(Commands(bot))