import importlib
from decimal import Decimal
from decimal import InvalidOperation
from typing import Optional
from typing import Tuple

import disnake
from disnake.ext import commands

import common.models as models
import common.utils as utils


class PointCMDs(commands.Cog, name="Point"):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    async def _clear_person(
        self, user_id: int, deny_in_game: bool = False, set_in_game: bool = False
    ):
        points = await models.MiniKGPoints.get_or_none(user_id=user_id)
        if points:
            if deny_in_game and points.in_game:
                return None

            points.points = points.rollover_points
            points.rollover_points = Decimal(0)

            if set_in_game:
                points.in_game = True

            await points.save()
            return points
        else:
            if set_in_game:
                return await models.MiniKGPoints.create(
                    user_id=user_id, points=0, in_game=True
                )
            else:
                return await models.MiniKGPoints.create(user_id=user_id, points=0)

    @commands.slash_command(
        name="add-points",
        description="Adds points to the members specified.",
        guild_ids=[786609181855318047],
        default_permission=False,
    )
    @commands.guild_permissions(786609181855318047, roles=utils.ADMIN_PERMS)
    async def add_points(
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
            default=1, description="How many points should be added/removed."
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

        async for points in models.MiniKGPoints.filter(
            user_id__in=frozenset(m.id for m in members)
        ).select_for_update():
            points.points += actual_count
            await points.save()

        if actual_count == Decimal(1):
            embed = disnake.Embed(
                color=self.bot.color,
                description=f"{', '.join(tuple(m.mention for m in members))} "
                + "got **1** point!",
            )
        else:
            embed = disnake.Embed(
                color=self.bot.color,
                description=f"{', '.join(tuple(m.mention for m in members))} "
                + f"got **{actual_count}** points!",
            )

        await inter.send(embed=embed)

    @commands.slash_command(
        name="remove-points",
        description="Removes points from the members specified.",
        guild_ids=[786609181855318047],
        default_permission=False,
    )
    @commands.guild_permissions(786609181855318047, roles=utils.ADMIN_PERMS)
    async def remove_points(
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
            default=1, description="How many points should be added/removed."
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

        async for points in models.MiniKGPoints.filter(
            user_id__in=frozenset(m.id for m in members)
        ).select_for_update():

            points.points -= actual_count
            if points.points < Decimal(0):
                points.points == Decimal(0)

            await points.save()

        if actual_count == Decimal(1):
            embed = disnake.Embed(
                color=self.bot.color,
                description="Removed **1** point from: "
                + f"{', '.join(tuple(m.mention for m in members))}.",
            )
        else:
            embed = disnake.Embed(
                color=self.bot.color,
                description=f"Removed **{actual_count}** points "
                + f"from: {', '.join(tuple(m.mention for m in members))}.",
            )

        await inter.send(embed=embed)

    @commands.slash_command(
        name="add-to-rollover",
        description="Adds points to the members' total points.",
        guild_ids=[786609181855318047],
        default_permission=False,
    )
    @commands.guild_permissions(786609181855318047, roles=utils.ADMIN_PERMS)
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
            default=1, description="How many points should be added/removed."
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

        async for points in models.MiniKGPoints.filter(
            user_id__in=frozenset(m.id for m in members)
        ).select_for_update():
            points.rollover_points += actual_count
            await points.save()

        if actual_count == Decimal(1):
            embed = disnake.Embed(
                color=self.bot.color,
                description=f"{', '.join(tuple(m.mention for m in members))} "
                + "got **1** added to their rollover points!",
            )
        else:
            embed = disnake.Embed(
                color=self.bot.color,
                description=f"{', '.join(tuple(m.mention for m in members))} "
                + f"got **{actual_count}** added to their rollover points!",
            )

        await inter.send(embed=embed)

    @commands.slash_command(
        name="remove-from-rollover",
        description="Removes points from the members' rollover points.",
        guild_ids=[786609181855318047],
        default_permission=False,
    )
    @commands.guild_permissions(786609181855318047, roles=utils.ADMIN_PERMS)
    async def remove_from_rollover(
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
            default=1, description="How many points should be added/removed."
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

        async for points in models.MiniKGPoints.filter(
            user_id__in=frozenset(m.id for m in members)
        ).select_for_update():

            points.rollover_points -= actual_count
            if points.rollover_points < Decimal(0):
                points.rollover_points == Decimal(0)

            await points.save()

        if actual_count == Decimal(1):
            embed = disnake.Embed(
                color=self.bot.color,
                description="Removed **1** from the rollover points "
                + f"of: {', '.join(tuple(m.mention for m in members))}.",
            )
        else:
            embed = disnake.Embed(
                color=self.bot.color,
                description=f"Removed **{actual_count}** from the rollover "
                f"points of: {', '.join(tuple(m.mention for m in members))}.",
            )

        await inter.send(embed=embed)

    @commands.slash_command(
        name="list-points",
        description="Lists out points for everyone still alive.",
        guild_ids=[786609181855318047],
        default_permission=False,
    )
    @commands.guild_permissions(786609181855318047, roles=utils.ADMIN_PERMS)
    async def list_points(self, inter: disnake.GuildCommandInteraction):
        await inter.response.defer(ephemeral=True)

        points = await models.MiniKGPoints.filter(in_game=True)
        points.sort(key=lambda i: i.points, reverse=True)
        list_inters = tuple(
            f"<@{p.user_id}>: **{p.points}** ({p.rollover_points} rollover)"
            for p in points
        )

        embed = disnake.Embed(
            color=self.bot.color,
            description="\n".join(list_inters),
            timestamp=disnake.utils.utcnow(),
        )
        embed.set_footer(text="As of")
        await inter.send(embed=embed, ephemeral=True)

    @commands.slash_command(
        name="reset-points",
        description="Resets everyone's points and removes them from the game.",
        guild_ids=[786609181855318047],
        default_permission=False,
    )
    @commands.guild_permissions(786609181855318047, roles=utils.ADMIN_PERMS)
    async def reset_points(self, inter: disnake.GuildCommandInteraction):
        await inter.response.defer()

        await models.MiniKGPoints.all().update(points=0, in_game=False)
        await inter.send("Done!")

    @commands.slash_command(
        name="remove-player-from-points",
        description="Removes a player from the points tracker.",
        guild_ids=[786609181855318047],
        default_permission=False,
    )
    @commands.guild_permissions(786609181855318047, roles=utils.ADMIN_PERMS)
    async def remove_player_from_points(
        self,
        inter: disnake.GuildCommandInteraction,
        user: disnake.User = commands.Param(description="The user to remove."),
    ):
        await inter.response.defer()

        points = await models.MiniKGPoints.get_or_none(user_id=user.id, in_game=True)

        if points:
            points.in_game = False
            await points.save()
            await inter.send(f"{user.mention} removed!",)
        else:
            await inter.send(
                embed=utils.error_embed_generate(
                    f"Member {user.mention} does not exist in the points system!"
                )
            )

    @commands.slash_command(
        name="add-player-to-points",
        description="Adds a player to the points tracker.",
        guild_ids=[786609181855318047],
        default_permission=False,
    )
    @commands.guild_permissions(786609181855318047, roles=utils.ADMIN_PERMS)
    async def add_player_to_points(
        self,
        inter: disnake.GuildCommandInteraction,
        user: disnake.User = commands.Param(description="The user to add."),
    ):
        await inter.response.defer()

        points = await self._clear_person(user.id, deny_in_game=True, set_in_game=True)
        if not points:
            await inter.send("This person is already in the KG!")
        else:
            await inter.send(f"Added {user.mention}!")

    @commands.slash_command(
        name="setup-minikg-points",
        description="Sets up points for everyone with the Mini-KG Participant role.",
        guild_ids=[786609181855318047],
        default_permission=False,
    )
    @commands.guild_permissions(786609181855318047, roles=utils.ADMIN_PERMS)
    async def setup_minikg_points(self, inter: disnake.GuildCommandInteraction):
        await inter.response.defer()

        participant_role = inter.guild.get_role(939993631140495360)
        for member in participant_role.members:
            await self._clear_person(member.id, set_in_game=True)

        await inter.send("Done!")

    @commands.slash_command(
        name="points",
        description="List your points for the current Mini-KG.",
        guild_ids=[786609181855318047],
        default_permission=False,
    )
    @commands.guild_permissions(786609181855318047, roles=utils.MINI_KG_PERMS)
    async def points(self, inter: disnake.GuildCommandInteraction):
        await inter.response.defer(ephemeral=True)

        points = await models.MiniKGPoints.get_or_none(
            user_id=inter.author.id, in_game=True
        )
        if points:
            embed = disnake.Embed(
                color=self.bot.color,
                description=f"You have **{points.points}** points!"
                + f"\nYou have {points.rollover_points} points that will"
                + " be added next time you play.",
                timestamp=disnake.utils.utcnow(),
            )
            embed.set_footer(text="As of")
            await inter.send(embed=embed, ephemeral=True)
        else:
            await inter.send(
                embed=utils.error_embed_generate("You aren't in the KG!"),
                ephemeral=True,
            )


def setup(bot):
    importlib.reload(utils)
    bot.add_cog(PointCMDs(bot))
