import importlib
import time
from typing import TYPE_CHECKING

import dateutil.parser
import naff
import pytz

import common.utils as utils

et = pytz.timezone("US/Eastern")

if TYPE_CHECKING:
    from datetime import datetime

    class TimeParser(datetime):
        ...

else:

    class TimeParser(naff.Converter):
        async def convert(self, ctx: naff.Context, argument: str):
            try:
                the_time = dateutil.parser.parse(argument, ignoretz=True, fuzzy=True)
                the_time = et.localize(the_time)
                return the_time.astimezone(pytz.utc)
            except dateutil.parser.ParserError:
                raise naff.errors.BadArgument(
                    "The argument provided could not be parsed as a time!"
                )


class Etc(utils.Extension):
    def __init__(self, bot: naff.Client):
        self.bot = bot
        self.display_name = "Misc."

    @naff.slash_command(
        name="ping",
        description=(
            "Pings the bot. Great way of finding out if the bot’s working, but has no"
            " real use."
        ),
        scopes=[786609181855318047],
    )
    async def ping(self, ctx: naff.InteractionContext):
        await ctx.defer()

        start_time = time.perf_counter()
        ping_discord = round((self.bot.latency * 1000), 2)

        mes = await ctx.send(
            content=(
                f"Pong!\n`{ping_discord}` ms from Discord.\nCalculating personal"
                " ping..."
            ),
        )

        end_time = time.perf_counter()
        ping_personal = round(((end_time - start_time) * 1000), 2)

        await mes.edit(
            content=(
                f"Pong!\n`{ping_discord}` ms from Discord.\n`{ping_personal}` ms"
                " personally."
            )
        )

    @naff.prefixed_command(aliases=["format_time"])
    @utils.proper_permissions()
    async def time_format(self, ctx: naff.PrefixedContext, *, time: TimeParser):
        """Formats the time given into the fancy Discord timestamp markdown.
        Every time is assumed to be in ET.
        Times with no dates are assumed to be taking place today."""
        timestamp = naff.Timestamp.fromdatetime(time)
        time_str = timestamp.format("f")
        await ctx.send(time_str)


def setup(bot):
    importlib.reload(utils)
    Etc(bot)
