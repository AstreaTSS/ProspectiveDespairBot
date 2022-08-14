import asyncio
import importlib
import random
import time

import naff

import common.utils as utils


class Etc(utils.Extension):
    def __init__(self, bot: naff.Client):
        self.bot = bot
        self.name = "Misc."
        self.rp_channels: set[naff.GuildText] = set()

        asyncio.create_task(self.async_init())

    async def async_init(self):
        await self.bot.wait_until_ready()

        CATEGORIES = {921451746897829938}
        CHANNELS = {1007124952736079893}
        EXCLUDE = {}

        for category_id in CATEGORIES:
            category: naff.GuildCategory = self.bot.get_channel(category_id)  # type: ignore

            for channel in category.text_channels:
                if int(channel.id) not in EXCLUDE:
                    self.rp_channels.add(channel)

        for channel_id in CHANNELS:
            channel: naff.GuildText = self.bot.get_channel(channel_id)  # type: ignore
            if int(channel.id) not in EXCLUDE:
                self.rp_channels.add(channel)

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

    @naff.slash_command(
        name="pick-location",
        description="Randomly picks a location in the KG.",
        scopes=[786609181855318047],
    )
    async def pick_location(self, ctx: naff.InteractionContext):
        chan = random.choice(tuple(self.rp_channels))
        await ctx.send(chan.mention)


def setup(bot):
    importlib.reload(utils)
    Etc(bot)
