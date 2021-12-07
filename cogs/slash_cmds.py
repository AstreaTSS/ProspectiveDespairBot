import asyncio
import importlib
import typing
from decimal import Decimal
from decimal import InvalidOperation
from typing import Optional
from typing import Tuple

import discord
import dislash
from discord.ext import commands

import common.cards as cards
import common.models as models
import common.utils as utils


admin_perms = dislash.SlashCommandPermissions.from_ids(
    {786610218133094420: True}, {229350299909881876: True}
)

alive_player_perms = dislash.SlashCommandPermissions.from_ids(
    {786610218133094420: True, 786610731826544670: True}, {229350299909881876: True}
)

interaction_options = [
    dislash.Option("user_1", "The first user.", dislash.OptionType.USER, True),
    dislash.Option("user_2", "The second user.", dislash.OptionType.USER, False),
    dislash.Option("user_3", "The third user.", dislash.OptionType.USER, False),
    dislash.Option("user_4", "The fourth user.", dislash.OptionType.USER, False),
    dislash.Option("user_5", "The fifth user.", dislash.OptionType.USER, False),
    dislash.Option("user_6", "The sixth user.", dislash.OptionType.USER, False),
    dislash.Option("user_7", "The seventh user.", dislash.OptionType.USER, False),
    dislash.Option("user_8", "The eight user.", dislash.OptionType.USER, False),
    dislash.Option("user_9", "The ninth user.", dislash.OptionType.USER, False),
    dislash.Option("user_10", "The tenth user.", dislash.OptionType.USER, False),
    dislash.Option("user_11", "The eleventh user.", dislash.OptionType.USER, False),
    dislash.Option("user_12", "The twelfth user.", dislash.OptionType.USER, False),
    dislash.Option("user_13", "The thirteenth user.", dislash.OptionType.USER, False),
    dislash.Option("user_14", "The fourteenth user.", dislash.OptionType.USER, False),
    dislash.Option("user_15", "The fifteenth user.", dislash.OptionType.USER, False),
]

interactions_plus = interaction_options.copy()
interactions_plus.append(
    dislash.Option(
        "count",
        "How many interactions should be added/removed.",
        dislash.OptionType.NUMBER,
        False,
    )
)


class SlashCMDS(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.loop = self.bot.loop.create_task(self.add_perms())

    def cog_unload(self) -> None:
        self.loop.cancel()

    async def add_perms(self):
        await asyncio.sleep(10)
        slash_cmds: typing.List[
            dislash.SlashCommand
        ] = await self.bot.slash.fetch_guild_commands(786609181855318047)

        perm_dict = {
            cmd.id: alive_player_perms if cmd.name == "interactions" else admin_perms
            for cmd in slash_cmds
        }

        await self.bot.slash.batch_edit_guild_command_permissions(
            786609181855318047, perm_dict
        )

    @dislash.slash_command(
        name="add-interaction",
        description="Adds an interaction to the members specified.",
        guild_ids=[786609181855318047],
        default_permission=False,
        options=interactions_plus,
    )
    async def add_interaction(
        self,
        inter: dislash.Interaction,
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
        user_11: Optional[discord.User] = None,
        user_12: Optional[discord.User] = None,
        user_13: Optional[discord.User] = None,
        user_14: Optional[discord.User] = None,
        user_15: Optional[discord.User] = None,
        count: Optional[float] = None,
    ):
        await inter.create_response(type=5)

        if count is None:
            count = 1

        try:
            actual_count = Decimal(count)
        except InvalidOperation:
            raise dislash.BadArgument("Number provided is not a decimal!")

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
            user_11,
            user_12,
            user_13,
            user_14,
            user_15,
        )
        members: Tuple[discord.User, ...] = tuple(
            user for user in all_users if user is not None
        )

        async for interact in models.UserInteraction.filter(
            user_id__in=frozenset(m.id for m in members)
        ).select_for_update():
            interact.interactions += actual_count
            interact.total_interactions += actual_count
            await interact.save()

        if actual_count == Decimal(1):
            embed = discord.Embed(
                color=self.bot.color,
                description=f"{', '.join(tuple(m.mention for m in members))} "
                + "got **1** interaction!",
            )
        else:
            embed = discord.Embed(
                color=self.bot.color,
                description=f"{', '.join(tuple(m.mention for m in members))} "
                + f"got **{actual_count}** interactions!",
            )

        await inter.edit(embed=embed)

    @dislash.slash_command(
        name="remove-interaction",
        description="Removes an interaction from the members specified.",
        guild_ids=[786609181855318047],
        default_permission=False,
        options=interactions_plus,
    )
    async def remove_interaction(
        self,
        inter: dislash.Interaction,
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
        user_11: Optional[discord.User] = None,
        user_12: Optional[discord.User] = None,
        user_13: Optional[discord.User] = None,
        user_14: Optional[discord.User] = None,
        user_15: Optional[discord.User] = None,
        count: Optional[float] = None,
    ):
        await inter.create_response(type=5)

        if count is None:
            count = 1

        try:
            actual_count = Decimal(count)
        except InvalidOperation:
            raise dislash.BadArgument("Number provided is not a decimal!")

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
            user_11,
            user_12,
            user_13,
            user_14,
            user_15,
        )
        members: Tuple[discord.User, ...] = tuple(
            user for user in all_users if user is not None
        )

        async for interact in models.UserInteraction.filter(
            user_id__in=frozenset(m.id for m in members)
        ).select_for_update():

            interact.interactions -= actual_count
            if interact.interactions < Decimal(0):
                interact.interactions == Decimal(0)

            interact.total_interactions -= actual_count
            if interact.total_interactions < Decimal(0):
                interact.total_interactions == Decimal(0)

            await interact.save()

        if actual_count == Decimal(1):
            embed = discord.Embed(
                color=self.bot.color,
                description="Removed **1** interaction from: "
                + f"{', '.join(tuple(m.mention for m in members))}.",
            )
        else:
            embed = discord.Embed(
                color=self.bot.color,
                description=f"Removed **{actual_count}** interactions "
                + f"from: {', '.join(tuple(m.mention for m in members))}.",
            )

        await inter.edit(embed=embed)

    @dislash.slash_command(
        name="add-event",
        description="Gives an event point to the users specified.",
        guild_ids=[786609181855318047],
        default_permission=False,
        options=interaction_options,
    )
    async def add_event(
        self,
        inter: dislash.Interaction,
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
        user_11: Optional[discord.User] = None,
        user_12: Optional[discord.User] = None,
        user_13: Optional[discord.User] = None,
        user_14: Optional[discord.User] = None,
        user_15: Optional[discord.User] = None,
    ):
        await inter.create_response(type=5)

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
            user_11,
            user_12,
            user_13,
            user_14,
            user_15,
        )
        members: Tuple[discord.User, ...] = tuple(
            user for user in all_users if user is not None
        )

        async for interact in models.UserInteraction.filter(
            user_id__in=frozenset(m.id for m in members)
        ).select_for_update():
            interact.interactions += Decimal("0.5")
            interact.total_interactions += Decimal("0.5")
            await interact.save()

        embed = discord.Embed(
            color=self.bot.color,
            description=f"{', '.join(tuple(m.mention for m in members))} have been recorded to be "
            + "at the event! They get **0.5** interaction points.",
        )

        await inter.edit(embed=embed)

    @dislash.slash_command(
        name="add-to-total",
        description="Adds an interaction to the members' total interactions.",
        guild_ids=[673355251583025192],
        default_permission=False,
        options=interactions_plus,
    )
    async def add_to_total(
        self,
        inter: dislash.Interaction,
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
        user_11: Optional[discord.User] = None,
        user_12: Optional[discord.User] = None,
        user_13: Optional[discord.User] = None,
        user_14: Optional[discord.User] = None,
        user_15: Optional[discord.User] = None,
        count: Optional[float] = None,
    ):
        await inter.create_response(type=5)

        if count is None:
            count = 1

        try:
            actual_count = Decimal(count)
        except InvalidOperation:
            raise dislash.BadArgument("Number provided is not a decimal!")

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
            user_11,
            user_12,
            user_13,
            user_14,
            user_15,
        )
        members: Tuple[discord.User, ...] = tuple(
            user for user in all_users if user is not None
        )

        async for interact in models.UserInteraction.filter(
            user_id__in=frozenset(m.id for m in members)
        ).select_for_update():
            interact.total_interactions += actual_count
            await interact.save()

        if actual_count == Decimal(1):
            embed = discord.Embed(
                color=self.bot.color,
                description=f"{', '.join(tuple(m.mention for m in members))} "
                + "got **1** added to their total interactions!",
            )
        else:
            embed = discord.Embed(
                color=self.bot.color,
                description=f"{', '.join(tuple(m.mention for m in members))} "
                + f"got **{actual_count}** added to their total interactions!",
            )

        await inter.edit(embed=embed)

    @dislash.slash_command(
        name="remove-from-total",
        description="Removes an interaction from the members' total interactions.",
        guild_ids=[673355251583025192],
        default_permission=False,
        options=interactions_plus,
    )
    async def remove_from_total(
        self,
        inter: dislash.Interaction,
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
        user_11: Optional[discord.User] = None,
        user_12: Optional[discord.User] = None,
        user_13: Optional[discord.User] = None,
        user_14: Optional[discord.User] = None,
        user_15: Optional[discord.User] = None,
        count: Optional[float] = None,
    ):
        await inter.create_response(type=5)

        if count is None:
            count = 1

        try:
            actual_count = Decimal(count)
        except InvalidOperation:
            raise dislash.BadArgument("Number provided is not a decimal!")

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
            user_11,
            user_12,
            user_13,
            user_14,
            user_15,
        )
        members: Tuple[discord.User, ...] = tuple(
            user for user in all_users if user is not None
        )

        async for interact in models.UserInteraction.filter(
            user_id__in=frozenset(m.id for m in members)
        ).select_for_update():

            interact.total_interactions -= actual_count
            if interact.total_interactions < Decimal(0):
                interact.total_interactions == Decimal(0)

            await interact.save()

        if actual_count == Decimal(1):
            embed = discord.Embed(
                color=self.bot.color,
                description="Removed **1** from the total interactions "
                + f"of: {', '.join(tuple(m.mention for m in members))}.",
            )
        else:
            embed = discord.Embed(
                color=self.bot.color,
                description=f"Removed **{actual_count}** from the total "
                f"interactions of: {', '.join(tuple(m.mention for m in members))}.",
            )

        await inter.edit(embed=embed)

    @dislash.slash_command(
        name="list-interactions",
        description="Lists out interactions for everyone still alive.",
        guild_ids=[786609181855318047],
        default_permission=False,
        options=[],
    )
    async def list_interactions(self, inter: dislash.Interaction):
        await inter.create_response(type=5, ephemeral=True)

        inters = await models.UserInteraction.all()
        inters.sort(key=lambda i: i.interactions, reverse=True)
        list_inters = tuple(
            f"<@{i.user_id}>: **{i.interactions}** ({i.total_interactions} total)"
            for i in inters
        )

        embed = discord.Embed(
            color=self.bot.color,
            description="\n".join(list_inters),
            timestamp=discord.utils.utcnow(),
        )
        embed.set_footer(text="As of")
        await inter.edit(embed=embed)

    @dislash.slash_command(
        name="reset-interactions",
        description="Resets everyone's interaction counts.",
        guild_ids=[786609181855318047],
        default_permission=False,
        options=[],
    )
    async def reset_interactions(self, inter: dislash.Interaction):
        await inter.create_response(type=5)

        # keeps parity with old way of functioning
        # removes any not-alive player from here
        not_alive_user_ids = tuple(
            c.user_id for c in cards.participants if c.status != cards.Status.ALIVE
        )
        await models.UserInteraction.filter(user_id__in=not_alive_user_ids).delete()

        await models.UserInteraction.all().update(interactions=0)
        await inter.edit("Done!")

    @dislash.slash_command(
        name="remove-player-from-interaction",
        description="Removes a player from the interaction tracker.",
        guild_ids=[786609181855318047],
        default_permission=False,
        options=[
            dislash.Option(
                "user", "The user to remove.", dislash.OptionType.USER, True
            ),
        ],
    )
    async def remove_player_from_interaction(
        self, inter: dislash.Interaction, user: discord.User
    ):
        await inter.create_response(type=5)

        num_deleted = await models.UserInteraction.filter(user_id=user.id).delete()
        if num_deleted > 0:
            await inter.edit(
                f"{user.mention} deleted!",
                allowed_mentions=utils.deny_mentions(inter.author),
            )
        else:
            await inter.edit(
                embed=utils.error_embed_generate(
                    f"Member {user.mention} does not exist in interactions!"
                )
            )

    @dislash.slash_command(
        name="add-player-to-interaction",
        description="Adds a player to the interaction tracker.",
        guild_ids=[786609181855318047],
        default_permission=False,
        options=[
            dislash.Option("user", "The user to add.", dislash.OptionType.USER, True),
        ],
    )
    async def add_player_to_interaction(
        self, inter: dislash.Interaction, user: discord.User
    ):
        await inter.create_response(type=5)

        exists = await models.UserInteraction.exists(user_id=user.id)
        if exists:
            await inter.edit(
                embed=utils.error_embed_generate(
                    f"Member {user.mention} already in interactions!"
                )
            )
            return

        await models.UserInteraction.create(user_id=user.id, interactions=0)
        await inter.edit(
            f"Added {user.mention}!", allowed_mentions=utils.deny_mentions(inter.author)
        )

    @dislash.slash_command(
        name="refresh-players-for-interactions",
        description="COMPLETELY deletes old interaction data and adds in new players.",
        guild_ids=[786609181855318047],
        default_permission=False,
        options=[],
    )
    async def refresh_players_for_interactions(self, inter: dislash.Interaction):
        await inter.create_response(type=5)

        await models.UserInteraction.all().delete()
        user_ids = tuple(
            c.user_id for c in cards.participants if c.status == cards.Status.ALIVE
        )
        for user_id in user_ids:
            await models.UserInteraction.create(
                user_id=user_id, interactions=0, total_interactions=0
            )

        await inter.edit("Done!")

    @dislash.slash_command(
        name="interactions",
        description="List your interactions for this activity cycle.",
        guild_ids=[786609181855318047],
        default_permission=False,
        permissions=alive_player_perms,
        options=[],
    )
    async def interactions(self, inter: dislash.Interaction):
        await inter.create_response(type=5, ephemeral=True)

        interact = await models.UserInteraction.get_or_none(user_id=inter.author.id)
        if interact:
            embed = discord.Embed(
                color=self.bot.color,
                description=f"You have **{interact.interactions}** interactions for this cycle!"
                + f"\n*You have had {interact.total_interactions} interactions throughout the "
                + "entire season.*",
                timestamp=discord.utils.utcnow(),
            )
            embed.set_footer(text="As of")
            await inter.edit(embed=embed)
        else:
            await inter.edit(embed=utils.error_embed_generate("You aren't in the KG!"))

    @commands.Cog.listener()
    async def on_slash_command_error(
        self, inter: dislash.SlashInteraction, error: dislash.ApplicationCommandError
    ):
        if isinstance(
            error,
            (
                dislash.BadArgument,
                dislash.InteractionCheckFailure,
                dislash.NotGuildOwner,
            ),
        ):
            await inter.create_response(
                embed=utils.error_embed_generate(str(error)), ephemeral=True
            )
        elif "Unknown interaction" in str(error):
            await inter.channel.send(
                f"{inter.author.mention}, the bot is a bit slow and so cannot do slash commands "
                + "right now. Please wait a bit and try again.",
                delete_after=3,
            )
        else:
            await utils.error_handle(self.bot, error, inter)


def setup(bot):
    importlib.reload(utils)
    bot.add_cog(SlashCMDS(bot))
