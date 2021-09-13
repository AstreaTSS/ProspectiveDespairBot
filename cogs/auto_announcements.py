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

        self.webhook_session = aiohttp.ClientSession()

        self.webhook = discord.Webhook.from_url(
            os.environ.get("WEBHOOK_URL"), session=self.webhook_session,
        )

        self.task = self.bot.loop.create_task(self.auto_run())

    def cog_unload(self):
        self.task.cancel()
        self.bot.loop.create_task(self.webhook_session.close())

    def gen_embed(self, day: bool = True):
        embed = discord.Embed(title="Announcement from Talia Aelius", color=0x155F60)
        if day:
            str_builder = [
                "Wake up, sweeties~ it's 9 AM!\n",
                "The cafeteria and kitchen are now open for your eating "
                "pleasure~ we wouldn't want to die on an empty stomach, would we?",
                "\n\nRemember: escape is only a murder away~",
            ]
        else:
            str_builder = [
                "It's 11 PM, sweeties~ time to go to sleep!\n",
                "The cafeteria and kitchen will close in a few minutes. ",
                "I would move out of there if you don't want to be shot to ",
                "death~ it's not exciting as murder or being murder, after all!",
                "\n\nRemember: escape is only a murder away, especially at night~",
            ]
        embed.description = "".join(str_builder)
        return embed

    @commands.command(
        aliases=["run_night_announce", "night_announcement", "night_announce"]
    )
    @utils.proper_permissions()
    async def run_night_announcement(self, ctx: commands.Context):
        await self.webhook.send(embed=self.gen_embed(day=False))
        await ctx.reply("Done!")

    @commands.command(aliases=["run_day_announce", "day_announcement", "day_announce"])
    @utils.proper_permissions()
    async def run_day_announcement(self, ctx: commands.Context):
        await self.webhook.send(embed=self.gen_embed(day=True))
        await ctx.reply("Done!")

    async def auto_run(self):
        while True:
            et_now = datetime.datetime.now(et)

            # very hacky way of finding out when to sleep based on the current time
            if et_now.hour == 23:
                sleep_till = et_now + relativedelta(
                    days=+1, hour=9, minute=0, second=0, microsecond=0
                )
            elif 0 <= et_now.hour < 9:
                sleep_till = et_now + relativedelta(
                    hour=9, minute=0, second=0, microsecond=0
                )
            else:
                sleep_till = et_now + relativedelta(
                    hour=23, minute=0, second=0, microsecond=0
                )

            await discord.utils.sleep_until(sleep_till)
            et_now = datetime.datetime.now(et)

            embed = self.gen_embed(day=bool(et_now.hour != 23))
            await self.webhook.send(embed=embed)
            await asyncio.sleep(3600)


def setup(bot):
    importlib.reload(utils)
    bot.add_cog(AutoAnnouncements(bot))
