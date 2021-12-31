import importlib
from decimal import Decimal
from decimal import InvalidOperation
from typing import Optional
from typing import Tuple

import disnake
from disnake.ext import commands

import common.cards as cards
import common.models as models
import common.utils as utils


class InteractionCMDs(commands.Cog, name="Interaction"):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.slash_command(
        name="add-interaction",
        description="Adds an interaction to the members specified.",
        guild_ids=[673355251583025192],
        default_permission=False,
    )
    @commands.guild_permissions(673355251583025192, roles=utils.ADMIN_PERMS)
    async def add_interaction(
        self,
        inter: disnake.GuildCommandInteraction,
        user_1: disnake.User = commands.Param(description="The first user."),
        user_2: Optional[disnake.User] = commands.Param(
            default=None, description="The second user."
        ),
        user_3: Optional[disnake.User] = commands.Param(
            default=None, description="The third user."
        ),
        user_4: Optional[disnake.User] = commands.Param(
            default=None, description="The fourth user."
        ),
        user_5: Optional[disnake.User] = commands.Param(
            default=None, description="The fifth user."
        ),
        user_6: Optional[disnake.User] = commands.Param(
            default=None, description="The sixth user."
        ),
        user_7: Optional[disnake.User] = commands.Param(
            default=None, description="The seventh user."
        ),
        user_8: Optional[disnake.User] = commands.Param(
            default=None, description="The eight user."
        ),
        user_9: Optional[disnake.User] = commands.Param(
            default=None, description="The ninth user."
        ),
        user_10: Optional[disnake.User] = commands.Param(
            default=None, description="The tenth user."
        ),
        user_11: Optional[disnake.User] = commands.Param(
            default=None, description="The eleventh user."
        ),
        user_12: Optional[disnake.User] = commands.Param(
            default=None, description="The twelfth user."
        ),
        user_13: Optional[disnake.User] = commands.Param(
            default=None, description="The thirteenth user."
        ),
        user_14: Optional[disnake.User] = commands.Param(
            default=None, description="The fourteenth user."
        ),
        user_15: Optional[disnake.User] = commands.Param(
            default=None, description="The fifteenth user."
        ),
        count: float = commands.Param(
            default=1, description="How many interactions should be added/removed."
        ),
    ):
        await inter.response.defer()

        try:
            actual_count = Decimal(count)
        except InvalidOperation:
            raise commands.BadArgument("Number provided is not a decimal!")

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
        members: Tuple[disnake.User, ...] = tuple(
            user for user in all_users if user is not None
        )

        async for interact in models.UserInteraction.filter(
            user_id__in=frozenset(m.id for m in members)
        ).select_for_update():
            interact.interactions += actual_count
            interact.total_interactions += actual_count
            await interact.save()

        if actual_count == Decimal(1):
            embed = disnake.Embed(
                color=self.bot.color,
                description=f"{', '.join(tuple(m.mention for m in members))} "
                + "got **1** interaction!",
            )
        else:
            embed = disnake.Embed(
                color=self.bot.color,
                description=f"{', '.join(tuple(m.mention for m in members))} "
                + f"got **{actual_count}** interactions!",
            )

        await inter.send(embed=embed)

    @commands.slash_command(
        name="remove-interaction",
        description="Removes an interaction from the members specified.",
        guild_ids=[673355251583025192],
        default_permission=False,
    )
    @commands.guild_permissions(673355251583025192, roles=utils.ADMIN_PERMS)
    async def remove_interaction(
        self,
        inter: disnake.GuildCommandInteraction,
        user_1: disnake.User = commands.Param(description="The first user."),
        user_2: Optional[disnake.User] = commands.Param(
            default=None, description="The second user."
        ),
        user_3: Optional[disnake.User] = commands.Param(
            default=None, description="The third user."
        ),
        user_4: Optional[disnake.User] = commands.Param(
            default=None, description="The fourth user."
        ),
        user_5: Optional[disnake.User] = commands.Param(
            default=None, description="The fifth user."
        ),
        user_6: Optional[disnake.User] = commands.Param(
            default=None, description="The sixth user."
        ),
        user_7: Optional[disnake.User] = commands.Param(
            default=None, description="The seventh user."
        ),
        user_8: Optional[disnake.User] = commands.Param(
            default=None, description="The eight user."
        ),
        user_9: Optional[disnake.User] = commands.Param(
            default=None, description="The ninth user."
        ),
        user_10: Optional[disnake.User] = commands.Param(
            default=None, description="The tenth user."
        ),
        user_11: Optional[disnake.User] = commands.Param(
            default=None, description="The eleventh user."
        ),
        user_12: Optional[disnake.User] = commands.Param(
            default=None, description="The twelfth user."
        ),
        user_13: Optional[disnake.User] = commands.Param(
            default=None, description="The thirteenth user."
        ),
        user_14: Optional[disnake.User] = commands.Param(
            default=None, description="The fourteenth user."
        ),
        user_15: Optional[disnake.User] = commands.Param(
            default=None, description="The fifteenth user."
        ),
        count: float = commands.Param(
            default=1, description="How many interactions should be added/removed."
        ),
    ):
        await inter.response.defer()

        try:
            actual_count = Decimal(count)
        except InvalidOperation:
            raise commands.BadArgument("Number provided is not a decimal!")

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
        members: Tuple[disnake.User, ...] = tuple(
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
            embed = disnake.Embed(
                color=self.bot.color,
                description="Removed **1** interaction from: "
                + f"{', '.join(tuple(m.mention for m in members))}.",
            )
        else:
            embed = disnake.Embed(
                color=self.bot.color,
                description=f"Removed **{actual_count}** interactions "
                + f"from: {', '.join(tuple(m.mention for m in members))}.",
            )

        await inter.send(embed=embed)

    @commands.slash_command(
        name="add-event",
        description="Gives an event point to the users specified.",
        guild_ids=[673355251583025192],
        default_permission=False,
    )
    @commands.guild_permissions(673355251583025192, roles=utils.ADMIN_PERMS)
    async def add_event(
        self,
        inter: disnake.GuildCommandInteraction,
        user_1: disnake.User = commands.Param(description="The first user."),
        user_2: Optional[disnake.User] = commands.Param(
            default=None, description="The second user."
        ),
        user_3: Optional[disnake.User] = commands.Param(
            default=None, description="The third user."
        ),
        user_4: Optional[disnake.User] = commands.Param(
            default=None, description="The fourth user."
        ),
        user_5: Optional[disnake.User] = commands.Param(
            default=None, description="The fifth user."
        ),
        user_6: Optional[disnake.User] = commands.Param(
            default=None, description="The sixth user."
        ),
        user_7: Optional[disnake.User] = commands.Param(
            default=None, description="The seventh user."
        ),
        user_8: Optional[disnake.User] = commands.Param(
            default=None, description="The eight user."
        ),
        user_9: Optional[disnake.User] = commands.Param(
            default=None, description="The ninth user."
        ),
        user_10: Optional[disnake.User] = commands.Param(
            default=None, description="The tenth user."
        ),
        user_11: Optional[disnake.User] = commands.Param(
            default=None, description="The eleventh user."
        ),
        user_12: Optional[disnake.User] = commands.Param(
            default=None, description="The twelfth user."
        ),
        user_13: Optional[disnake.User] = commands.Param(
            default=None, description="The thirteenth user."
        ),
        user_14: Optional[disnake.User] = commands.Param(
            default=None, description="The fourteenth user."
        ),
        user_15: Optional[disnake.User] = commands.Param(
            default=None, description="The fifteenth user."
        ),
    ):
        await inter.response.defer()

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
        members: Tuple[disnake.User, ...] = tuple(
            user for user in all_users if user is not None
        )

        async for interact in models.UserInteraction.filter(
            user_id__in=frozenset(m.id for m in members)
        ).select_for_update():
            interact.interactions += Decimal("0.5")
            interact.total_interactions += Decimal("0.5")
            await interact.save()

        embed = disnake.Embed(
            color=self.bot.color,
            description=f"{', '.join(tuple(m.mention for m in members))} have been recorded to be "
            + "at the event! They get **0.5** interaction points.",
        )

        await inter.send(embed=embed)

    @commands.slash_command(
        name="add-to-total",
        description="Adds an interaction to the members' total interactions.",
        guild_ids=[673355251583025192],
        default_permission=False,
    )
    @commands.guild_permissions(673355251583025192, roles=utils.ADMIN_PERMS)
    async def add_to_total(
        self,
        inter: disnake.GuildCommandInteraction,
        user_1: disnake.User = commands.Param(description="The first user."),
        user_2: Optional[disnake.User] = commands.Param(
            default=None, description="The second user."
        ),
        user_3: Optional[disnake.User] = commands.Param(
            default=None, description="The third user."
        ),
        user_4: Optional[disnake.User] = commands.Param(
            default=None, description="The fourth user."
        ),
        user_5: Optional[disnake.User] = commands.Param(
            default=None, description="The fifth user."
        ),
        user_6: Optional[disnake.User] = commands.Param(
            default=None, description="The sixth user."
        ),
        user_7: Optional[disnake.User] = commands.Param(
            default=None, description="The seventh user."
        ),
        user_8: Optional[disnake.User] = commands.Param(
            default=None, description="The eight user."
        ),
        user_9: Optional[disnake.User] = commands.Param(
            default=None, description="The ninth user."
        ),
        user_10: Optional[disnake.User] = commands.Param(
            default=None, description="The tenth user."
        ),
        user_11: Optional[disnake.User] = commands.Param(
            default=None, description="The eleventh user."
        ),
        user_12: Optional[disnake.User] = commands.Param(
            default=None, description="The twelfth user."
        ),
        user_13: Optional[disnake.User] = commands.Param(
            default=None, description="The thirteenth user."
        ),
        user_14: Optional[disnake.User] = commands.Param(
            default=None, description="The fourteenth user."
        ),
        user_15: Optional[disnake.User] = commands.Param(
            default=None, description="The fifteenth user."
        ),
        count: float = commands.Param(
            default=1, description="How many interactions should be added/removed."
        ),
    ):
        await inter.response.defer()

        try:
            actual_count = Decimal(count)
        except InvalidOperation:
            raise commands.BadArgument("Number provided is not a decimal!")

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
        members: Tuple[disnake.User, ...] = tuple(
            user for user in all_users if user is not None
        )

        async for interact in models.UserInteraction.filter(
            user_id__in=frozenset(m.id for m in members)
        ).select_for_update():
            interact.total_interactions += actual_count
            await interact.save()

        if actual_count == Decimal(1):
            embed = disnake.Embed(
                color=self.bot.color,
                description=f"{', '.join(tuple(m.mention for m in members))} "
                + "got **1** added to their total interactions!",
            )
        else:
            embed = disnake.Embed(
                color=self.bot.color,
                description=f"{', '.join(tuple(m.mention for m in members))} "
                + f"got **{actual_count}** added to their total interactions!",
            )

        await inter.send(embed=embed)

    @commands.slash_command(
        name="remove-from-total",
        description="Removes an interaction from the members' total interactions.",
        guild_ids=[673355251583025192],
        default_permission=False,
    )
    @commands.guild_permissions(673355251583025192, roles=utils.ADMIN_PERMS)
    async def remove_from_total(
        self,
        inter: disnake.GuildCommandInteraction,
        user_1: disnake.User = commands.Param(description="The first user."),
        user_2: Optional[disnake.User] = commands.Param(
            default=None, description="The second user."
        ),
        user_3: Optional[disnake.User] = commands.Param(
            default=None, description="The third user."
        ),
        user_4: Optional[disnake.User] = commands.Param(
            default=None, description="The fourth user."
        ),
        user_5: Optional[disnake.User] = commands.Param(
            default=None, description="The fifth user."
        ),
        user_6: Optional[disnake.User] = commands.Param(
            default=None, description="The sixth user."
        ),
        user_7: Optional[disnake.User] = commands.Param(
            default=None, description="The seventh user."
        ),
        user_8: Optional[disnake.User] = commands.Param(
            default=None, description="The eight user."
        ),
        user_9: Optional[disnake.User] = commands.Param(
            default=None, description="The ninth user."
        ),
        user_10: Optional[disnake.User] = commands.Param(
            default=None, description="The tenth user."
        ),
        user_11: Optional[disnake.User] = commands.Param(
            default=None, description="The eleventh user."
        ),
        user_12: Optional[disnake.User] = commands.Param(
            default=None, description="The twelfth user."
        ),
        user_13: Optional[disnake.User] = commands.Param(
            default=None, description="The thirteenth user."
        ),
        user_14: Optional[disnake.User] = commands.Param(
            default=None, description="The fourteenth user."
        ),
        user_15: Optional[disnake.User] = commands.Param(
            default=None, description="The fifteenth user."
        ),
        count: float = commands.Param(
            default=1, description="How many interactions should be added/removed."
        ),
    ):
        await inter.response.defer()

        if count is None:
            count = 1

        try:
            actual_count = Decimal(count)
        except InvalidOperation:
            raise commands.BadArgument("Number provided is not a decimal!")

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
        members: Tuple[disnake.User, ...] = tuple(
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
            embed = disnake.Embed(
                color=self.bot.color,
                description="Removed **1** from the total interactions "
                + f"of: {', '.join(tuple(m.mention for m in members))}.",
            )
        else:
            embed = disnake.Embed(
                color=self.bot.color,
                description=f"Removed **{actual_count}** from the total "
                f"interactions of: {', '.join(tuple(m.mention for m in members))}.",
            )

        await inter.send(embed=embed)

    @commands.slash_command(
        name="list-interactions",
        description="Lists out interactions for everyone still alive.",
        guild_ids=[673355251583025192],
        default_permission=False,
    )
    @commands.guild_permissions(673355251583025192, roles=utils.ADMIN_PERMS)
    async def list_interactions(self, inter: disnake.GuildCommandInteraction):
        await inter.response.defer(ephemeral=True)

        inters = await models.UserInteraction.all()
        inters.sort(key=lambda i: i.interactions, reverse=True)
        list_inters = tuple(
            f"<@{i.user_id}>: **{i.interactions}** ({i.total_interactions} total)"
            for i in inters
        )

        embed = disnake.Embed(
            color=self.bot.color,
            description="\n".join(list_inters),
            timestamp=disnake.utils.utcnow(),
        )
        embed.set_footer(text="As of")
        await inter.send(embed=embed, ephemeral=True)

    @commands.slash_command(
        name="reset-interactions",
        description="Resets everyone's interaction counts.",
        guild_ids=[673355251583025192],
        default_permission=False,
    )
    @commands.guild_permissions(673355251583025192, roles=utils.ADMIN_PERMS)
    async def reset_interactions(self, inter: disnake.GuildCommandInteraction):
        await inter.response.defer()

        # keeps parity with old way of functioning
        # removes any not-alive player from here
        not_alive_user_ids = tuple(
            c.user_id for c in cards.participants if c.status != cards.Status.ALIVE
        )
        await models.UserInteraction.filter(user_id__in=not_alive_user_ids).delete()

        await models.UserInteraction.all().update(interactions=0)
        await inter.send("Done!")

    @commands.slash_command(
        name="remove-player-from-interaction",
        description="Removes a player from the interaction tracker.",
        guild_ids=[673355251583025192],
        default_permission=False,
    )
    @commands.guild_permissions(673355251583025192, roles=utils.ADMIN_PERMS)
    async def remove_player_from_interaction(
        self,
        inter: disnake.GuildCommandInteraction,
        user: disnake.User = commands.Param(description="The user to remove."),
    ):
        await inter.response.defer()

        num_deleted = await models.UserInteraction.filter(user_id=user.id).delete()
        if num_deleted > 0:
            await inter.send(f"{user.mention} deleted!",)
        else:
            await inter.send(
                embed=utils.error_embed_generate(
                    f"Member {user.mention} does not exist in interactions!"
                )
            )

    @commands.slash_command(
        name="add-player-to-interaction",
        description="Adds a player to the interaction tracker.",
        guild_ids=[673355251583025192],
        default_permission=False,
    )
    @commands.guild_permissions(673355251583025192, roles=utils.ADMIN_PERMS)
    async def add_player_to_interaction(
        self,
        inter: disnake.GuildCommandInteraction,
        user: disnake.User = commands.Param(description="The user to add."),
    ):
        await inter.response.defer()

        exists = await models.UserInteraction.exists(user_id=user.id)
        if exists:
            await inter.send(
                embed=utils.error_embed_generate(
                    f"Member {user.mention} already in interactions!"
                )
            )
            return

        await models.UserInteraction.create(user_id=user.id, interactions=0)
        await inter.send(f"Added {user.mention}!")

    @commands.slash_command(
        name="refresh-players-for-interactions",
        description="COMPLETELY deletes old interaction data and adds in new players.",
        guild_ids=[673355251583025192],
        default_permission=False,
    )
    @commands.guild_permissions(673355251583025192, roles=utils.ADMIN_PERMS)
    async def refresh_players_for_interactions(
        self, inter: disnake.GuildCommandInteraction
    ):
        await inter.response.defer()

        await models.UserInteraction.all().delete()
        user_ids = tuple(
            c.user_id for c in cards.participants if c.status == cards.Status.ALIVE
        )
        for user_id in user_ids:
            await models.UserInteraction.create(
                user_id=user_id, interactions=0, total_interactions=0
            )

        await inter.send("Done!")

    @commands.slash_command(
        name="interactions",
        description="List your interactions for this activity cycle.",
        guild_ids=[673355251583025192],
        default_permission=False,
    )
    @commands.guild_permissions(673355251583025192, roles=utils.ALIVE_PLAYER_PERMS)
    async def interactions(self, inter: disnake.GuildCommandInteraction):
        await inter.response.defer(ephemeral=True)

        interact = await models.UserInteraction.get_or_none(user_id=inter.author.id)
        if interact:
            embed = disnake.Embed(
                color=self.bot.color,
                description=f"You have **{interact.interactions}** interactions for this cycle!"
                + f"\n*You have had {interact.total_interactions} interactions throughout the "
                + "entire season.*",
                timestamp=disnake.utils.utcnow(),
            )
            embed.set_footer(text="As of")
            await inter.send(embed=embed, ephemeral=True)
        else:
            await inter.send(
                embed=utils.error_embed_generate("You aren't in the KG!"),
                ephemeral=True,
            )

    @commands.Cog.listener()
    async def on_slash_command_error(
        self, inter: disnake.GuildCommandInteraction, error: commands.CommandError
    ):
        if isinstance(error, commands.BadArgument):
            await inter.send(
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
    bot.add_cog(InteractionCMDs(bot))
