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
from discord_slash.model import SlashCommandOptionType
from discord_slash.model import SlashCommandPermissionType
from discord_slash.utils.manage_commands import create_option
from discord_slash.utils.manage_commands import create_permission

import common.cards as cards
import common.models as models
import common.utils as utils


admin_perms = {
    673355251583025192: [
        create_permission(673635882271637516, SlashCommandPermissionType.ROLE, True),
        create_permission(673630805343600641, SlashCommandPermissionType.ROLE, True),
    ]
}

alive_player_perms = {
    673355251583025192: [
        create_permission(673635882271637516, SlashCommandPermissionType.ROLE, True),
        create_permission(673630805343600641, SlashCommandPermissionType.ROLE, True),
        create_permission(673640411494875182, SlashCommandPermissionType.ROLE, True),
    ]
}

interaction_options = [
    create_option("user_1", "The first user.", SlashCommandOptionType.USER, True),
    create_option("user_2", "The second user.", SlashCommandOptionType.USER, False),
    create_option("user_3", "The third user.", SlashCommandOptionType.USER, False),
    create_option("user_4", "The fourth user.", SlashCommandOptionType.USER, False),
    create_option("user_5", "The fifth user.", SlashCommandOptionType.USER, False),
    create_option("user_6", "The sixth user.", SlashCommandOptionType.USER, False),
    create_option("user_7", "The seventh user.", SlashCommandOptionType.USER, False),
    create_option("user_8", "The eight user.", SlashCommandOptionType.USER, False),
    create_option("user_9", "The ninth user.", SlashCommandOptionType.USER, False),
    create_option("user_10", "The tenth user.", SlashCommandOptionType.USER, False),
]

interactions_plus = interaction_options.copy()
interactions_plus.append(
    create_option("count", "How many interactions should be added.", 3, False,)
)


class SlashCMDS(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @cog_ext.cog_slash(
        name="add-interaction",
        description="Adds an interaction to the members specified.",
        guild_ids=[673355251583025192],
        default_permission=False,
        permissions=admin_perms,
        options=interactions_plus,
    )
    async def add_interaction(
        self,
        ctx: SlashContext,
        user_1: discord.User,
        user_2: Optional[discord.User] = None,
        user_3: Optional[discord.User] = None,
        user_4: Optional[discord.User] = None,
        user_5: Optional[discord.User] = None,
        user_6: Optional[discord.User] = None,
        user_7: Optional[discord.User] = None,
        user_8: Optional[discord.User] = None,
        user_9: Optional[discord.User] = None,
        user_10: Optional[discord.User] = None,
        count: Optional[str] = None,
    ):
        await ctx.defer()

        if count is None:
            count = "1"

        try:
            actual_count = Decimal(count)
        except InvalidOperation:
            await ctx.send(
                embed=utils.error_embed_generate("Number provided is not a decimal!")
            )
            return

        all_users = (
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

        if actual_count == Decimal(1):
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
        name="remove-interaction",
        description="Removes an interaction from the members specified.",
        guild_ids=[673355251583025192],
        default_permission=False,
        permissions=admin_perms,
        options=interactions_plus,
    )
    async def remove_interaction(
        self,
        ctx: SlashContext,
        user_1: discord.User,
        user_2: Optional[discord.User] = None,
        user_3: Optional[discord.User] = None,
        user_4: Optional[discord.User] = None,
        user_5: Optional[discord.User] = None,
        user_6: Optional[discord.User] = None,
        user_7: Optional[discord.User] = None,
        user_8: Optional[discord.User] = None,
        user_9: Optional[discord.User] = None,
        user_10: Optional[discord.User] = None,
        count: Optional[str] = None,
    ):
        await ctx.defer()

        if count is None:
            count = "1"

        try:
            actual_count = Decimal(count)
        except InvalidOperation:
            await ctx.send(
                embed=utils.error_embed_generate("Number provided is not a decimal!")
            )
            return

        all_users = (
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
            inter.interactions -= count
            if inter.interactions < Decimal(0):
                inter.interactions == Decimal(0)
            await inter.save()

        if actual_count == Decimal(1):
            embed = discord.Embed(
                color=self.bot.color,
                description=f"Removed an interaction from: {', '.join(tuple(m.mention for m in members))}.",
            )
        else:
            embed = discord.Embed(
                color=self.bot.color,
                description=f"Removed {actual_count} interactions from: {', '.join(tuple(m.mention for m in members))}.",
            )

        await ctx.send(embed=embed)

    @cog_ext.cog_slash(
        name="add-event",
        description="Gives an event point to the users specified.",
        guild_ids=[673355251583025192],
        default_permission=False,
        permissions=admin_perms,
        options=interaction_options,
    )
    async def add_event(
        self,
        ctx: SlashContext,
        user_1: discord.User,
        user_2: Optional[discord.User] = None,
        user_3: Optional[discord.User] = None,
        user_4: Optional[discord.User] = None,
        user_5: Optional[discord.User] = None,
        user_6: Optional[discord.User] = None,
        user_7: Optional[discord.User] = None,
        user_8: Optional[discord.User] = None,
        user_9: Optional[discord.User] = None,
        user_10: Optional[discord.User] = None,
    ):
        await ctx.defer()

        all_users = (
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
        guild_ids=[673355251583025192],
        default_permission=False,
        permissions=alive_player_perms,
        options=[],
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
                embed=utils.error_embed_generate("You aren't in the KG!"), hidden=True
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
    bot.add_cog(SlashCMDS(bot))
