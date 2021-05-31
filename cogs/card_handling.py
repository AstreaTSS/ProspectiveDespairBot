import importlib
from datetime import datetime

import discord
import asyncio
from discord.ext import commands

import common.cards as cards

class CardHandling(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.command()
    @commands.is_owner()
    async def update_cast(self, ctx: commands.Context):

        async with ctx.typing():
            profile_chan = self.bot.get_channel(786638377801744394)

            def is_valid(m: discord.Message):
                return m.author.id == self.bot.user.id

            reference_date = datetime(2021, 5, 29)
            await profile_chan.purge(limit=100, check=is_valid, after=reference_date)

            await profile_chan.send("```\nKG Hosts\n```")

            for host_card in cards.hosts:
                embed = await host_card.as_embed(ctx.bot)
                await profile_chan.send(embed=embed)
                await asyncio.sleep(1) # ratelimits

            await profile_chan.send("```\nParticipants\n```")

            for participant_card in cards.participants:
                embed = await participant_card.as_embed(ctx.bot)
                await profile_chan.send(embed=embed)
                await asyncio.sleep(1)

            await profile_chan.send("All participant cards should be in alphabetical order and easily searchable.\n" +
            #"All host cards should be displayed in the order in which they were revealed.\n"
            "If any information is wrong, ping or DM Sonic about it and he'll change it ASAP.")

        await ctx.reply("Done!")


def setup(bot):
    importlib.reload(cards)
    bot.add_cog(CardHandling(bot))