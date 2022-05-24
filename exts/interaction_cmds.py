import importlib
from decimal import Decimal
from decimal import InvalidOperation
from typing import Optional
from typing import Tuple

import naff

import common.cards as cards
import common.models as models
import common.utils as utils


user_options = [
    naff.SlashCommandOption("user_1", naff.OptionTypes.USER, "The first user."),  # type: ignore
    naff.SlashCommandOption(
        "user_2", naff.OptionTypes.USER, "The second user.", required=False  # type: ignore
    ),
    naff.SlashCommandOption(
        "user_3", naff.OptionTypes.USER, "The third user.", required=False  # type: ignore
    ),
    naff.SlashCommandOption(
        "user_4", naff.OptionTypes.USER, "The fourth user.", required=False  # type: ignore
    ),
    naff.SlashCommandOption(
        "user_5", naff.OptionTypes.USER, "The fifth user.", required=False  # type: ignore
    ),
    naff.SlashCommandOption(
        "user_6", naff.OptionTypes.USER, "The sixth user.", required=False  # type: ignore
    ),
    naff.SlashCommandOption(
        "user_7", naff.OptionTypes.USER, "The seventh user.", required=False  # type: ignore
    ),
    naff.SlashCommandOption(
        "user_8", naff.OptionTypes.USER, "The eighth user.", required=False  # type: ignore
    ),
    naff.SlashCommandOption(
        "user_9", naff.OptionTypes.USER, "The ninth user.", required=False  # type: ignore
    ),
    naff.SlashCommandOption(
        "user_10", naff.OptionTypes.USER, "The tenth user.", required=False  # type: ignore
    ),
    naff.SlashCommandOption(
        "user_11", naff.OptionTypes.USER, "The eleventh user.", required=False  # type: ignore
    ),
    naff.SlashCommandOption(
        "user_12", naff.OptionTypes.USER, "The twelfth user.", required=False  # type: ignore
    ),
    naff.SlashCommandOption(
        "user_13", naff.OptionTypes.USER, "The thirteenth user.", required=False  # type: ignore
    ),
    naff.SlashCommandOption(
        "user_14", naff.OptionTypes.USER, "The fourteenth user.", required=False  # type: ignore
    ),
    naff.SlashCommandOption(
        "user_15", naff.OptionTypes.USER, "The fifteenth user.", required=False  # type: ignore
    ),
]

user_and_count = user_options.copy()
user_and_count.append(
    naff.SlashCommandOption(
        "count",  # type: ignore
        naff.OptionTypes.NUMBER,
        "How many interactions should be added/removed.",  # type: ignore
        required=False,
    )
)


class InteractionCMDs(utils.Extension):
    def __init__(self, bot):
        self.bot: naff.Client = bot
        self.name = "Interaction"

    @naff.slash_command(
        name="add-interaction",
        description="Adds an interaction to the members specified.",
        options=user_and_count,
        scopes=[786609181855318047],
        default_member_permissions=naff.Permissions.ADMINISTRATOR,
    )
    async def add_interaction(
        self,
        ctx: naff.InteractionContext,
        user_1: naff.User,
        user_2: Optional[naff.User] = None,
        user_3: Optional[naff.User] = None,
        user_4: Optional[naff.User] = None,
        user_5: Optional[naff.User] = None,
        user_6: Optional[naff.User] = None,
        user_7: Optional[naff.User] = None,
        user_8: Optional[naff.User] = None,
        user_9: Optional[naff.User] = None,
        user_10: Optional[naff.User] = None,
        user_11: Optional[naff.User] = None,
        user_12: Optional[naff.User] = None,
        user_13: Optional[naff.User] = None,
        user_14: Optional[naff.User] = None,
        user_15: Optional[naff.User] = None,
        count: float = 1,
    ):
        await ctx.defer()

        try:
            actual_count = Decimal(count)
        except InvalidOperation:
            raise naff.errors.BadArgument("Number provided is not a decimal!")

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
        members: Tuple[naff.User, ...] = tuple(
            user for user in all_users if user is not None
        )

        async for interact in models.UserInteraction.filter(
            user_id__in=frozenset(m.id for m in members)
        ).select_for_update():
            interact.interactions += actual_count
            interact.total_interactions += actual_count
            await interact.save()

        if actual_count == Decimal(1):
            embed = naff.Embed(
                color=self.bot.color,
                description=f"{', '.join(tuple(m.mention for m in members))} "
                + "got **1** interaction!",
            )
        else:
            embed = naff.Embed(
                color=self.bot.color,
                description=f"{', '.join(tuple(m.mention for m in members))} "
                + f"got **{actual_count}** interactions!",
            )

        await ctx.send(embed=embed)

    @naff.slash_command(
        name="remove-interaction",
        description="Removes an interaction from the members specified.",
        options=user_and_count,
        scopes=[786609181855318047],
        default_member_permissions=naff.Permissions.ADMINISTRATOR,
    )
    async def remove_interaction(
        self,
        ctx: naff.InteractionContext,
        user_1: naff.User,
        user_2: Optional[naff.User] = None,
        user_3: Optional[naff.User] = None,
        user_4: Optional[naff.User] = None,
        user_5: Optional[naff.User] = None,
        user_6: Optional[naff.User] = None,
        user_7: Optional[naff.User] = None,
        user_8: Optional[naff.User] = None,
        user_9: Optional[naff.User] = None,
        user_10: Optional[naff.User] = None,
        user_11: Optional[naff.User] = None,
        user_12: Optional[naff.User] = None,
        user_13: Optional[naff.User] = None,
        user_14: Optional[naff.User] = None,
        user_15: Optional[naff.User] = None,
        count: float = 1,
    ):
        await ctx.defer()

        try:
            actual_count = Decimal(count)
        except InvalidOperation:
            raise naff.errors.BadArgument("Number provided is not a decimal!")

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
        members: Tuple[naff.User, ...] = tuple(
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
            embed = naff.Embed(
                color=self.bot.color,
                description="Removed **1** interaction from: "
                + f"{', '.join(tuple(m.mention for m in members))}.",
            )
        else:
            embed = naff.Embed(
                color=self.bot.color,
                description=f"Removed **{actual_count}** interactions "
                + f"from: {', '.join(tuple(m.mention for m in members))}.",
            )

        await ctx.send(embed=embed)

    @naff.slash_command(
        name="add-event",
        description="Gives an event point to the users specified.",
        options=user_options,
        scopes=[786609181855318047],
        default_member_permissions=naff.Permissions.ADMINISTRATOR,
    )
    async def add_event(
        self,
        ctx: naff.InteractionContext,
        user_1: naff.User,
        user_2: Optional[naff.User] = None,
        user_3: Optional[naff.User] = None,
        user_4: Optional[naff.User] = None,
        user_5: Optional[naff.User] = None,
        user_6: Optional[naff.User] = None,
        user_7: Optional[naff.User] = None,
        user_8: Optional[naff.User] = None,
        user_9: Optional[naff.User] = None,
        user_10: Optional[naff.User] = None,
        user_11: Optional[naff.User] = None,
        user_12: Optional[naff.User] = None,
        user_13: Optional[naff.User] = None,
        user_14: Optional[naff.User] = None,
        user_15: Optional[naff.User] = None,
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
            user_11,
            user_12,
            user_13,
            user_14,
            user_15,
        )
        members: Tuple[naff.User, ...] = tuple(
            user for user in all_users if user is not None
        )

        async for interact in models.UserInteraction.filter(
            user_id__in=frozenset(m.id for m in members)
        ).select_for_update():
            interact.interactions += Decimal("0.5")
            interact.total_interactions += Decimal("0.5")
            await interact.save()

        embed = naff.Embed(
            color=self.bot.color,
            description=(
                f"{', '.join(tuple(m.mention for m in members))} have been recorded"
                " to be "
            )
            + "at the event! They get **0.5** interaction points.",
        )

        await ctx.send(embed=embed)

    @naff.slash_command(
        name="add-to-total",
        description="Adds an interaction to the members' total interactions.",
        options=user_and_count,
        scopes=[786609181855318047],
        default_member_permissions=naff.Permissions.ADMINISTRATOR,
    )
    async def add_to_total(
        self,
        ctx: naff.InteractionContext,
        user_1: naff.User,
        user_2: Optional[naff.User] = None,
        user_3: Optional[naff.User] = None,
        user_4: Optional[naff.User] = None,
        user_5: Optional[naff.User] = None,
        user_6: Optional[naff.User] = None,
        user_7: Optional[naff.User] = None,
        user_8: Optional[naff.User] = None,
        user_9: Optional[naff.User] = None,
        user_10: Optional[naff.User] = None,
        user_11: Optional[naff.User] = None,
        user_12: Optional[naff.User] = None,
        user_13: Optional[naff.User] = None,
        user_14: Optional[naff.User] = None,
        user_15: Optional[naff.User] = None,
        count: float = 1,
    ):
        await ctx.defer()

        try:
            actual_count = Decimal(count)
        except InvalidOperation:
            raise naff.errors.BadArgument("Number provided is not a decimal!")

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
        members: Tuple[naff.User, ...] = tuple(
            user for user in all_users if user is not None
        )

        async for interact in models.UserInteraction.filter(
            user_id__in=frozenset(m.id for m in members)
        ).select_for_update():
            interact.total_interactions += actual_count
            await interact.save()

        if actual_count == Decimal(1):
            embed = naff.Embed(
                color=self.bot.color,
                description=f"{', '.join(tuple(m.mention for m in members))} "
                + "got **1** added to their total interactions!",
            )
        else:
            embed = naff.Embed(
                color=self.bot.color,
                description=f"{', '.join(tuple(m.mention for m in members))} "
                + f"got **{actual_count}** added to their total interactions!",
            )

        await ctx.send(embed=embed)

    @naff.slash_command(
        name="remove-from-total",
        description="Removes an interaction from the members' total interactions.",
        options=user_and_count,
        scopes=[786609181855318047],
        default_member_permissions=naff.Permissions.ADMINISTRATOR,
    )
    async def remove_from_total(
        self,
        ctx: naff.InteractionContext,
        user_1: naff.User,
        user_2: Optional[naff.User] = None,
        user_3: Optional[naff.User] = None,
        user_4: Optional[naff.User] = None,
        user_5: Optional[naff.User] = None,
        user_6: Optional[naff.User] = None,
        user_7: Optional[naff.User] = None,
        user_8: Optional[naff.User] = None,
        user_9: Optional[naff.User] = None,
        user_10: Optional[naff.User] = None,
        user_11: Optional[naff.User] = None,
        user_12: Optional[naff.User] = None,
        user_13: Optional[naff.User] = None,
        user_14: Optional[naff.User] = None,
        user_15: Optional[naff.User] = None,
        count: float = 1,
    ):
        await ctx.defer()

        if count is None:
            count = 1

        try:
            actual_count = Decimal(count)
        except InvalidOperation:
            raise naff.errors.BadArgument("Number provided is not a decimal!")

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
        members: Tuple[naff.User, ...] = tuple(
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
            embed = naff.Embed(
                color=self.bot.color,
                description="Removed **1** from the total interactions "
                + f"of: {', '.join(tuple(m.mention for m in members))}.",
            )
        else:
            embed = naff.Embed(
                color=self.bot.color,
                description=(
                    f"Removed **{actual_count}** from the total "
                    f"interactions of: {', '.join(tuple(m.mention for m in members))}."
                ),
            )

        await ctx.send(embed=embed)

    @naff.slash_command(
        name="list-interactions",
        description="Lists out interactions for everyone still alive.",
        scopes=[786609181855318047],
        default_member_permissions=naff.Permissions.ADMINISTRATOR,
    )
    async def list_interactions(self, ctx: naff.InteractionContext):
        await ctx.defer(ephemeral=True)

        inters = await models.UserInteraction.all()
        inters.sort(key=lambda i: i.interactions, reverse=True)
        list_inters = tuple(
            f"<@{i.user_id}>: **{i.interactions}** ({i.total_interactions} total)"
            for i in inters
        )

        embed = naff.Embed(
            color=self.bot.color,
            description="\n".join(list_inters),
            timestamp=naff.Timestamp.utcnow(),
        )
        embed.set_footer(text="As of")
        await ctx.send(embed=embed, ephemeral=True)

    @naff.slash_command(
        name="reset-interactions",
        description="Resets everyone's interaction counts.",
        scopes=[786609181855318047],
        default_member_permissions=naff.Permissions.ADMINISTRATOR,
    )
    async def reset_interactions(self, ctx: naff.InteractionContext):
        await ctx.defer()

        # keeps parity with old way of functioning
        # removes any not-alive player from here
        not_alive_user_ids = tuple(
            c.user_id for c in cards.participants if c.status != cards.Status.ALIVE
        )
        await models.UserInteraction.filter(user_id__in=not_alive_user_ids).delete()

        await models.UserInteraction.all().update(interactions=0)
        await ctx.send("Done!")

    @naff.slash_command(
        name="remove-player-from-interaction",
        description="Removes a player from the interaction tracker.",
        scopes=[786609181855318047],
        default_member_permissions=naff.Permissions.ADMINISTRATOR,
    )
    @naff.slash_option("user", "The user to remove.", naff.OptionTypes.USER)
    async def remove_player_from_interaction(
        self, ctx: naff.InteractionContext, user: naff.User
    ):
        await ctx.defer()

        num_deleted = await models.UserInteraction.filter(user_id=user.id).delete()
        if num_deleted > 0:
            await ctx.send(
                f"{user.mention} deleted!",
            )
        else:
            await ctx.send(
                embed=utils.error_embed_generate(
                    f"Member {user.mention} does not exist in interactions!"
                )
            )

    @naff.slash_command(
        name="add-player-to-interaction",
        description="Adds a player to the interaction tracker.",
        scopes=[786609181855318047],
        default_member_permissions=naff.Permissions.ADMINISTRATOR,
    )
    @naff.slash_option("user", "The user to add.", naff.OptionTypes.USER)
    async def add_player_to_interaction(
        self,
        ctx: naff.InteractionContext,
        user: naff.User,
    ):
        await ctx.defer()

        exists = await models.UserInteraction.exists(user_id=user.id)
        if exists:
            await ctx.send(
                embed=utils.error_embed_generate(
                    f"Member {user.mention} already in interactions!"
                )
            )
            return

        await models.UserInteraction.create(user_id=user.id, interactions=0)
        await ctx.send(f"Added {user.mention}!")

    @naff.slash_command(
        name="refresh-players-for-interactions",
        description="COMPLETELY deletes old interaction data and adds in new players.",
        scopes=[786609181855318047],
        default_member_permissions=naff.Permissions.ADMINISTRATOR,
    )
    async def refresh_players_for_interactions(
        self,
        ctx: naff.InteractionContext,
    ):
        await ctx.defer()

        await models.UserInteraction.all().delete()
        user_ids = tuple(
            c.user_id for c in cards.participants if c.status == cards.Status.ALIVE
        )
        for user_id in user_ids:
            await models.UserInteraction.create(
                user_id=user_id, interactions=0, total_interactions=0
            )

        await ctx.send("Done!")

    @naff.slash_command(
        name="interactions",
        description="List your interactions for this activity cycle.",
        scopes=[786609181855318047],
        default_member_permissions=naff.Permissions.MANAGE_GUILD,  # this should be adjusted so that alive players can use it
    )
    async def interactions(self, ctx: naff.InteractionContext):
        await ctx.defer(ephemeral=True)

        interact = await models.UserInteraction.get_or_none(user_id=ctx.author.id)
        if interact:
            embed = naff.Embed(
                color=self.bot.color,
                description=(
                    f"You have **{interact.interactions}** interactions for this cycle!"
                )
                + f"\n*You have had {interact.total_interactions} interactions"
                " throughout the "
                + "entire season.*",
                timestamp=naff.Timestamp.utcnow(),
            )
            embed.set_footer(text="As of")
            await ctx.send(embed=embed, ephemeral=True)
        else:
            await ctx.send(
                embed=utils.error_embed_generate("You aren't in the KG!"),
                ephemeral=True,
            )


def setup(bot):
    importlib.reload(utils)
    InteractionCMDs(bot)
