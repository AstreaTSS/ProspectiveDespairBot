import datetime
import importlib
from decimal import Decimal

import discord
from discord.ext import commands

import common.cards as cards
import common.models as models
import common.utils as utils


class Interactions(commands.Cog, name="Interaction"):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.command(aliases=["add_inter"])
    @commands.is_owner()
    async def add_interaction(
        self,
        ctx: commands.Context,
        members: commands.Greedy[discord.Member],
        count: utils.DecimalConverter = Decimal(1),
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

    @commands.command(aliases=["remove_inter", "del_inter"])
    @commands.is_owner()
    async def remove_interaction(
        self,
        ctx: commands.Context,
        members: commands.Greedy[discord.Member],
        count: utils.DecimalConverter = Decimal(1),
    ):
        async with ctx.typing():
            async for inter in models.UserInteraction.filter(
                user_id__in=frozenset(m.id for m in members)
            ).select_for_update():
                inter.interactions -= count
                if inter.interactions < Decimal(0):
                    inter.interactions == Decimal(0)
                await inter.save()

            if count == Decimal(1):
                embed = discord.Embed(
                    color=self.bot.color,
                    description=f"Removed an interaction from: {', '.join(tuple(m.mention for m in members))}.",
                )
            else:
                embed = discord.Embed(
                    color=self.bot.color,
                    description=f"Removed {count} interactions from: {', '.join(tuple(m.mention for m in members))}.",
                )

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

    @commands.command(
        aliases=[
            "remove_player_from_inter",
            "remove_play_from_inter",
            "rm_play_from_inter",
        ]
    )
    @commands.is_owner()
    async def remove_player_from_interaction(
        self, ctx: commands.Context, user: discord.User
    ):
        async with ctx.typing():
            num_deleted = await models.UserInteraction.filter(user_id=user.id).delete()

        if num_deleted > 0:
            await ctx.reply(
                f"{user.mention} deleted!",
                allowed_mentions=utils.deny_mentions(ctx.author),
            )
        else:
            raise commands.BadArgument(
                f"Member {user.mention} does not exist in interactions!"
            )

    @commands.command(
        aliases=["add_player_to_inter", "add_play_to_inter",]
    )
    @commands.is_owner()
    async def add_player_to_interaction(
        self, ctx: commands.Context, user: discord.User
    ):
        async with ctx.typing():
            exists = await models.UserInteraction.exists(user_id=user.id)
            if exists:
                raise commands.BadArgument(
                    f"Member {user.mention} already in interactions!"
                )

            await models.UserInteraction.create(user_id=user.id, interactions=0)

        await ctx.reply(
            f"Added {user.mention}!", allowed_mentions=utils.deny_mentions(ctx.author)
        )


def setup(bot):
    importlib.reload(cards)
    importlib.reload(utils)
    bot.add_cog(Interactions(bot))
