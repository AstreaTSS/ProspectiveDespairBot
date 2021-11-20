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
        embed = discord.Embed(title="Announcement from Drake Aelius", color=11779669)
        if day:
            str_builder = [
                "Wake up, idiots.\nIt's now 9 AM. Unless you're a lazy ass, ",
                "you should probably get ready for the day.\n",
                "And yeah, the cafeteria and kitchen has been unlocked too.",
                "\n\nRemember: if you want to escape, all you have to do is ",
                "kill. If you can't convince yourself to do that... how weak.",
            ]
        else:
            str_builder = [
                "It's 11 PM. Go to sleep.\n",
                "The cafeteria and kitchen will close in a few minutes. Move out of it ",
                "quickly: it would be rather pathetic if you died just by being in it.",
                "\n\nRemember: all you have to do to escape is kill... ",
                "and I heard night time's the *perfect* time to kill.",
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
