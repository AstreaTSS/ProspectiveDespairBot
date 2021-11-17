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

    #     self.webhook_session = aiohttp.ClientSession()

    #     self.webhook = discord.Webhook.from_url(
    #         os.environ.get("WEBHOOK_URL"),
    #         session=self.webhook_session,
    #     )

    #     self.task = self.bot.loop.create_task(self.auto_run())

    # def cog_unload(self):
    #     self.task.cancel()
    #     self.webhook_session.close()

    def gen_embed(self, day: bool = True):
        embed = discord.Embed(title="Announcement from Monokuma", color=13632027)
        embed.set_image(
            url="https://cdn.discordapp.com/attachments/457939628209602560/861282169276072006/vlcsnap-2021-07-04-12h26m28s639.png"
        )

        if day:
            str_builder = [
                "Yodelay he puhuhuhu! It is now 8 AM and night time is officially ",
                "over! Time to rise and freeze and get ready for a yodelay great day!",
            ]
        else:
            str_builder = [
                "Ahem. This is an important announcement. It is now 10 PM. ",
                "As such, it is officially nighttime. Soon the doors to the ",
                "buffet will be locked, and entry at that point is strictly ",
                "prohibited. Okay then... sweet dreams, everyone! Good night, ",
                "sleep tight, *don’t let the bedbugs bite...*",
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

            et_now = datetime.datetime.now(et)
            embed = self.gen_embed(day=bool(et_now.hour != 23))
            await self.webhook.send(embed=embed)
            await asyncio.sleep(3600)


def setup(bot):
    importlib.reload(utils)
    bot.add_cog(AutoAnnouncements(bot))
