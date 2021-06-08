import datetime
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

    @commands.command(aliases=["add_inter"])
    @commands.is_owner()
    async def add_interaction(
        self,
        ctx: commands.Context,
        members: commands.Greedy[discord.Member],
        count: int = 1,
    ):
        async with ctx.typing():
            async for inter in models.UserInteraction.filter(
                user_id__in=frozenset(m.id for m in members)
            ).select_for_update():
                inter.interactions += count
                await inter.save()

            if count == 1:
                embed = discord.Embed(
                    color=self.bot.color,
                    description=f"{', '.join(tuple(m.mention for m in members))} got an interaction!",
                )
            else:
                embed = discord.Embed(
                    color=self.bot.color,
                    description=f"{', '.join(tuple(m.mention for m in members))} got {count} interactions!",
                )

            await ctx.message.delete()

        await ctx.send(embed=embed)

    @commands.command()
    @commands.is_owner()
    async def add_event(
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
                description=f"{', '.join(tuple(m.mention for m in members))} have been recorded to be "
                + "at the event! They get 0.5 interaction points.",
            )

            await ctx.message.delete()

        await ctx.send(embed=embed)

    @commands.command(aliases=["reset_inters", "reset-inter"])
    @commands.is_owner()
    async def reset_interactions(self, ctx: commands.Context):
        async with ctx.typing():
            await models.UserInteraction.all().delete()

            user_ids = tuple(
                c.user_id for c in cards.participants if c.status == cards.Status.ALIVE
            )

            for user_id in user_ids:
                await models.UserInteraction.create(user_id=user_id, interactions=0)

        await ctx.reply("Done!")

    @commands.command(aliases=["list_inters", "list-inter"])
    @commands.is_owner()
    async def list_interactions(self, ctx: commands.Context):
        async with ctx.typing():
            inters = await models.UserInteraction.all()
            inters.sort(key=lambda i: i.interactions, reverse=True)
            list_inters = tuple(f"<@{i.user_id}>: {i.interactions}" for i in inters)

        embed = discord.Embed(
            color=self.bot.color,
            description="\n".join(list_inters),
            timestamp=datetime.datetime.utcnow(),
        )
        embed.set_footer(text="As of")
        await ctx.reply(embed=embed)

    @commands.command(aliases=["inter", "inters", "interaction"])
    async def interactions(self, ctx: commands.Context):
        """Allows you to view the number of interactions you had in the current cycle.
        Will not work if you are not in the KG."""
        async with ctx.typing():
            inter = await models.UserInteraction.get_or_none(user_id=ctx.author.id)
            if inter:

                embed = discord.Embed(
                    color=self.bot.color,
                    description=f"You have {inter.interactions} interactions for this cycle!",
                    timestamp=datetime.datetime.utcnow(),
                )
                embed.set_footer(text="As of")
                await ctx.reply(embed=embed)
            else:
                raise utils.CustomCheckFailure("You aren't in the KG!")


def setup(bot):
    importlib.reload(cards)
    importlib.reload(utils)
    bot.add_cog(Interactions(bot))
