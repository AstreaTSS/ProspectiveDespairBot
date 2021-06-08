import importlib
from decimal import Decimal

import discord
from discord.ext import commands

import common.cards as cards
import common.models as models
import common.utils as utils


class Interactions(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.command(aliases=["inter"])
    @commands.is_owner()
    async def interaction(
        self, ctx: commands.Context, members: commands.Greedy[discord.Member]
    ):

        async with ctx.typing():
            async for inter in models.UserInteraction.filter(
                user_id__in=frozenset(m.id for m in members)
            ).select_for_update():
                inter.interactions += 1
                await inter.save()

            embed = discord.Embed(
                color=self.bot.color,
                description=f"{', '.join(tuple(m.mention for m in members))} got an interaction!",
            )

            await ctx.message.delete()

        await ctx.send(embed=embed)

    @commands.command()
    @commands.is_owner()
    async def event(
        self, ctx: commands.Context, members: commands.Greedy[discord.Member]
    ):

        async with ctx.typing():
            async for inter in models.UserInteraction.filter(
                user_id__in=frozenset(m.id for m in members)
            ).select_for_update():
                inter.interactions += Decimal("0.5")
                await inter.save()

            embed = discord.Embed(
                color=self.bot.color,
                description=f"{', '.join(tuple(m.mention for m in members))} have been recorded to be at the event!",
            )

            await ctx.message.delete()

        await ctx.send(embed=embed)

    @commands.command(aliases=["reset_inters"])
    @commands.is_owner()
    async def reset_interactions(self, ctx: commands.Context):

        async with ctx.typing():
            await models.UserInteraction.all().delete()

            user_ids = tuple(c.user_id for c in cards.participants)

            for user_id in user_ids:
                await models.UserInteraction.create(user_id=user_id, interactions=0)

        await ctx.reply("Done!")

    @commands.command(aliases=["list_inters"])
    @commands.is_owner()
    async def list_interactions(self, ctx: commands.Context):

        async with ctx.typing():
            inters = await models.UserInteraction.all()
            list_inters = tuple(f"<@{i.user_id}> - {i.interactions}" for i in inters)

        await ctx.reply(
            "\n".join(list_inters), allowed_mentions=utils.deny_mentions(ctx.author)
        )


def setup(bot):
    importlib.reload(cards)
    importlib.reload(utils)
    bot.add_cog(Interactions(bot))
