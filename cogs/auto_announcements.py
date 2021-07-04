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
            if et_now.hour >= 22:
                sleep_till = et_now + relativedelta(
                    days=+1, hour=8, minute=0, second=0, microsecond=0
                )
            elif 0 <= et_now.hour < 8:
                sleep_till = et_now + relativedelta(
                    hour=8, minute=0, second=0, microsecond=0
                )
            else:
                sleep_till = et_now + relativedelta(
                    hour=22, minute=0, second=0, microsecond=0
                )

            await discord.utils.sleep_until(sleep_till)

            embed = discord.Embed(
                title="Announcement from Monokuma", color=13632027
            )
            embed.set_image(url="https://cdn.discordapp.com/attachments/690643602312790118/691828682112630789/image0.jpg")
            et_now = datetime.datetime.now(et)

            if et_now.hour == 22:
                str_builder = [
                    "Ahem. This is an important announcement. It is now 10 PM. ",
                    "As such, it is officially nighttime. Soon the doors to the ",
                    "buffet will be locked, and entry at that point is strictly ",
                    "prohibited. Okay then... sweet dreams, everyone! Good night, ",
                    "sleep tight, *don’t let the bedbugs bite...*",

                ]
            else:
                str_builder = [
                    "Yodelay he puhuhuhu! It is now 8 AM and night time is officially ",
                    "over! Time to rise and freeze and get ready for a yodelay great day!",
                ]

            embed.description = "".join(str_builder)
            await self.webhook.send(embed=embed)
            await asyncio.sleep(3600)


def setup(bot):
    importlib.reload(utils)
    bot.add_cog(AutoAnnouncements(bot))
