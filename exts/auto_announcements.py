import asyncio
import datetime
import importlib
import os

import naff
import pytz
from dateutil.relativedelta import relativedelta

import common.utils as utils

et = pytz.timezone("US/Eastern")


class AutoAnnouncements(utils.Extension):
    def __init__(self, bot):
        self.bot: naff.Client = bot

        self.webhook = naff.Webhook.from_url(os.environ["WEBHOOK_URL"], self.bot)

        self.task = asyncio.create_task(self.auto_run())

    def drop(self):
        self.task.cancel()
        super().drop()

    def gen_embed(self, day: bool = True):
        embed = naff.Embed(title="Announcement from Mayumi Takimura", color=0xF4AEA2)
        if day:
            str_builder = [
                "Good morning~ but, like, if you're hearing this, you survived and now"
                " it's 9 AM, which is lame.\nI *guess* you can get ready for the day."
                " Like, brush your teeth, take a shower... but like, do whatever you"
                " need to do to get ready for murder! That's the most important part,"
                " hehe...\n\nRemember: if guys wanna escape or whatever, you just"
                " gotta kill!"
            ]
        else:
            str_builder = [
                "OMG guys, it's 11 PM, it's night time!\nI would say like go to sleep"
                " or whatever, but now's the perfect time to kill! Like, come on,"
                " imagine all of the murder plans you could do in the dark! *No would"
                " even know that you did it...*\n\nWell, if you're going to sleep"
                " anyways, good night or whatever, I guess."
            ]
        embed.description = "".join(str_builder)
        return embed

    @naff.slash_command(
        name="run-night-announcement",
        description="Runs the nighttime announcement automatically.",
        scopes=[786609181855318047],
        default_member_permissions=naff.Permissions.ADMINISTRATOR,
    )
    async def run_night_announcement(self, ctx: naff.InteractionContext):
        await self.webhook.send(embed=self.gen_embed(day=False))
        await ctx.send("Done!")

    @naff.slash_command(
        name="run-day-announcement",
        description="Runs the daytime announcement automatically.",
        scopes=[786609181855318047],
        default_member_permissions=naff.Permissions.ADMINISTRATOR,
    )
    async def run_day_announcement(self, ctx: naff.InteractionContext):
        await self.webhook.send(embed=self.gen_embed(day=True))
        await ctx.send("Done!")

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

            await utils.sleep_until(sleep_till)
            et_now = datetime.datetime.now(et)

            embed = self.gen_embed(day=et_now.hour < 12)
            await self.webhook.send(embed=embed)
            await asyncio.sleep(3600)


def setup(bot):
    importlib.reload(utils)
    AutoAnnouncements(bot)
