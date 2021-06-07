import importlib
from datetime import datetime
from typing import Union

import discord
import asyncio
from discord.ext import commands

import common.cards as cards
import common.fuzzys as fuzzys

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

            embed = discord.Embed(timestamp=datetime.utcnow())
            embed.set_footer(text="Last Updated")

            await profile_chan.send("All participant cards should be in alphabetical order and easily searchable.\n" +
            "All host cards should be displayed in the order in which they were revealed.\n"
            "If any information is wrong, ping or DM Sonic about it and he'll change it ASAP.",embed=embed)

        await ctx.reply("Done!")

    @commands.command()
    async def search(self, ctx: commands.Context, *, query: Union[fuzzys.FuzzyMemberConverter, fuzzys.FuzzyOCNameConverter]):
        card: cards.Card = discord.utils.get(cards.participants, user_id=query.id)

        if not card:
            await ctx.reply("That user does not have a card!")
        else:
            embed = await card.as_embed(self.bot)
            await ctx.reply(embed=embed)


def setup(bot):
    importlib.reload(cards)
    bot.add_cog(CardHandling(bot))