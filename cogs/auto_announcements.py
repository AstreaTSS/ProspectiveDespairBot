import asyncio
import datetime
import importlib
import os

import aiohttp
import discord
import pytz
from dateutil.relativedelta import relativedelta
from discord.ext import commands

import common.utils as utils

et = pytz.timezone("US/Eastern")


class AutoAnnouncements(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.webhook = discord.Webhook.from_url(
            os.environ.get("WEBHOOK_URL"),
            adapter=discord.AsyncWebhookAdapter(aiohttp.ClientSession()),
        )

        self.task = self.bot.loop.create_task(self.auto_run())

    def cog_unload(self):
        self.task.cancel()

    async def auto_run(self):
        while True:
            et_now = datetime.datetime.now(et)

            # very hacky way of finding out when to sleep based on the current time
            if et_now.hour == 23:
                sleep_till = et_now + relativedelta(
                    days=+1, hour=9, minute=0, microsecond=0
                )
            elif 0 <= et_now.hour < 9:
                sleep_till = et_now + relativedelta(hour=9, minute=0, microsecond=0)
            else:
                sleep_till = et_now + relativedelta(hour=23, minute=0, microsecond=0)

            await discord.utils.sleep_until(sleep_till)

            embed = discord.Embed(
                title="Announcement from Drake Aelius", color=11779669
            )
            et_now = datetime.datetime.now(et)

            if et_now.hour == 23:
                embed.description = """It's 11 PM. Go to sleep.
                The mess hall will close in a few minutes. Move out of it quickly: it would be rather \
                pathetic if you died just by being in it.

                Remember: all you have to do to escape is kill... and I heard night time's the \
                *perfect* time to kill."""
            else:
                embed.description = """Wake up, idiots.
                It's now 9 AM. Unless you're a lazy ass, you should probably get ready for the day. \
                And yeah, the mess hall has been unlocked too.

                Remember: if you want to escape, all you have to do is kill. If you can't convince \
                yourself to do that... how weak."""

            await self.webhook.send(embed=embed)
            await asyncio.sleep(3600)


def setup(bot):
    importlib.reload(utils)
    bot.add_cog(AutoAnnouncements(bot))
