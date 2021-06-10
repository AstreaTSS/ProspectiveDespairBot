import datetime
import importlib
from decimal import Decimal
from decimal import InvalidOperation
from typing import Optional
from typing import Tuple

import discord
from discord.ext import commands
from discord_slash import cog_ext
from discord_slash import SlashContext
from discord_slash.model import SlashCommandPermissionType
from discord_slash.utils.manage_commands import create_permission

import common.cards as cards
import common.models as models
import common.utils as utils


sonic_perms = {
    786609181855318047: [
        create_permission(229350299909881876, SlashCommandPermissionType.USER, True)
    ]
}


def error_embed_generate(error_msg):
    return discord.Embed(colour=discord.Colour.red(), description=error_msg)


class SlashCMDS(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @cog_ext.cog_slash(
        name="add_interaction",
        description="Adds an interaction to the members specified.",
        guild_ids=[786609181855318047],
        permissions=sonic_perms,
    )
    async def add_interaction(
        self,
        ctx: SlashContext,
        user_1: discord.User,
        user_2: Optional[discord.User],
        user_3: Optional[discord.User],
        user_4: Optional[discord.User],
        user_5: Optional[discord.User],
        user_6: Optional[discord.User],
        user_7: Optional[discord.User],
        user_8: Optional[discord.User],
        user_9: Optional[discord.User],
        user_10: Optional[discord.User],
        count: Optional[str],
    ):
        await ctx.defer()

        if count is None:
            count = "1"

        try:
            actual_count = Decimal(count)
        except InvalidOperation:
            await ctx.send(
                embed=error_embed_generate("Number provided is not a decimal!")
            )
            return

        all_users = tuple(
            user_1,
            user_2,
            user_3,
            user_4,
            user_5,
            user_6,
            user_7,
            user_8,
            user_9,
            user_10,
        )
        members: Tuple[discord.User] = tuple(
            user for user in all_users if user is not None
        )

        async for inter in models.UserInteraction.filter(
            user_id__in=frozenset(m.id for m in members)
        ).select_for_update():
            inter.interactions += actual_count
            await inter.save()

        if actual_count == 1:
            embed = discord.Embed(
                color=self.bot.color,
                description=f"{', '.join(tuple(m.mention for m in members))} got an interaction!",
            )
        else:
            embed = discord.Embed(
                color=self.bot.color,
                description=f"{', '.join(tuple(m.mention for m in members))} got {actual_count} interactions!",
            )

        await ctx.send(embed=embed)

    @cog_ext.cog_slash(
        name="add_event",
        description="Gives an event point to the users specified.",
        guild_ids=[786609181855318047],
        permissions=sonic_perms,
    )
    async def add_event(
        self,
        ctx: SlashContext,
        user_1: discord.User,
        user_2: Optional[discord.User],
        user_3: Optional[discord.User],
        user_4: Optional[discord.User],
        user_5: Optional[discord.User],
        user_6: Optional[discord.User],
        user_7: Optional[discord.User],
        user_8: Optional[discord.User],
        user_9: Optional[discord.User],
        user_10: Optional[discord.User],
    ):
        await ctx.defer()

        all_users = tuple(
            user_1,
            user_2,
            user_3,
            user_4,
            user_5,
            user_6,
            user_7,
            user_8,
            user_9,
            user_10,
        )
        members: Tuple[discord.User] = tuple(
            user for user in all_users if user is not None
        )

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

        await ctx.send(embed=embed)

    @cog_ext.cog_slash(
        name="interactions",
        description="List your interactions for this activity cycle.",
        guild_ids=[786609181855318047],
    )
    async def interactions(self, ctx: SlashContext):
        await ctx.defer(hidden=True)

        inter = await models.UserInteraction.get_or_none(user_id=ctx.author.id)
        if inter:
            embed = discord.Embed(
                color=self.bot.color,
                description=f"You have {inter.interactions} interactions for this cycle!",
                timestamp=datetime.datetime.utcnow(),
            )
            embed.set_footer(text="As of")
            await ctx.send(embed=embed, hidden=True)
        else:
            await ctx.send(
                embed=error_embed_generate("You aren't in the KG!"), hidden=True
            )

    @commands.Cog.listener()
    async def on_slash_command_error(self, ctx, ex):
        if isinstance(ex, discord.NotFound) and ex.text == "Unknown interaction":
            if isinstance(ctx.author, (discord.Member, discord.User)):
                author_str = ctx.author.mention
            else:
                author_str = f"<@{ctx.author}>"
            await ctx.channel.send(
                f"{author_str}, the bot is a bit slow and so cannot do slash commands right now. Please wait a bit and try again.",
                delete_after=3,
            )
        else:
            await utils.error_handle(self.bot, ex, ctx)


def setup(bot):
    importlib.reload(utils)
    importlib.reload(cards)
    importlib.reload(models)
    bot.add_cog(SlashCMDS(bot))
