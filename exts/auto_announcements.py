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

        # self.task = self.bot.loop.create_task(self.auto_run())

    def drop(self):
        # self.task.cancel()
        super().drop()

    def gen_embed(self, day: bool = True):
        embed = naff.Embed(title="Announcement from Drake Aelius", color=11779669)
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
                "The cafeteria and kitchen will close in a few minutes. Move out"
                " of it ",
                "quickly: it would be rather pathetic if you died just by being in it.",
                "\n\nRemember: all you have to do to escape is kill... ",
                "and I heard night time's the *perfect* time to kill.",
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
