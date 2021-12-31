import importlib
import time
from typing import TYPE_CHECKING

import dateutil.parser
import disnake
import pytz
from disnake.ext import commands

import common.utils as utils

et = pytz.timezone("US/Eastern")

if TYPE_CHECKING:
    from datetime import datetime

    class TimeParser(datetime):
        ...


else:

    class TimeParser(commands.Converter):
        async def convert(self, ctx: commands.Context, argument: str):
            try:
                the_time = dateutil.parser.parse(argument, ignoretz=True, fuzzy=True)
                the_time = et.localize(the_time)
                return the_time.astimezone(pytz.utc)
            except dateutil.parser.ParserError:
                raise commands.BadArgument(
                    "The argument provided could not be parsed as a time!"
                )


class Etc(commands.Cog, name="Misc."):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.member_role = disnake.Object(786610276606279680)

    @commands.slash_command(
        name="ping",
        description="Pings the bot. Great way of finding out if the bot’s working, but has no real use.",
        guild_ids=[786609181855318047],
    )
    async def ping(self, inter: disnake.GuildCommandInteraction):
        await inter.response.defer()

        start_time = time.perf_counter()
        ping_discord = round((self.bot.latency * 1000), 2)

        mes = await inter.edit_original_message(
            content=f"Pong!\n`{ping_discord}` ms from Discord.\nCalculating personal ping...",
        )

        end_time = time.perf_counter()
        ping_personal = round(((end_time - start_time) * 1000), 2)

        await mes.edit(
            content=f"Pong!\n`{ping_discord}` ms from Discord.\n`{ping_personal}` ms personally."
        )

    @commands.command(aliases=["format_time"])
    @utils.proper_permissions()
    async def time_format(self, ctx: commands.Context, *, time_str: TimeParser):
        """Formats the time given into the fancy Discord timestamp markdown.
        Every time is assumed to be in ET.
        Times with no dates are assumed to be taking place today."""
        await ctx.send(disnake.utils.format_dt(time_str))

    @commands.Cog.listener()
    async def on_member_update(self, before: disnake.Member, after: disnake.Member):
        if before.pending and not after.pending:
            await after.add_roles(self.member_role, reason="User has verified.")


def setup(bot):
    importlib.reload(utils)
    bot.add_cog(Etc(bot))
