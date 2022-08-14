import importlib
import time
from typing import TYPE_CHECKING

import dateutil.parser
import naff
import pytz

import common.utils as utils

et = pytz.timezone("US/Eastern")


class Etc(utils.Extension):
    def __init__(self, bot: naff.Client):
        self.bot = bot
        self.name = "Misc."

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


def setup(bot):
    importlib.reload(utils)
    Etc(bot)
