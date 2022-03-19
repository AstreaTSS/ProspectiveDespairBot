import asyncio
import datetime
import importlib
import os

import aiohttp
import disnake
import pytz
from dateutil.relativedelta import relativedelta
from disnake.ext import commands

import common.utils as utils

et = pytz.timezone("US/Eastern")


class AutoAnnouncements(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

        # self.webhook_session = aiohttp.ClientSession()

        # self.webhook = disnake.Webhook.from_url(
        #     os.environ.get("WEBHOOK_URL"), session=self.webhook_session,
        # )

        # self.task = self.bot.loop.create_task(self.auto_run())

    def cog_unload(self):
        pass
        # self.task.cancel()
        # self.bot.loop.create_task(self.webhook_session.close())

    def gen_embed(self, day: bool = True):
        embed = disnake.Embed(title="Announcement from Monokuma", color=13632027)
        embed.set_image(
            url="https://cdn.discordapp.com/attachments/457939628209602560/861282169276072006/vlcsnap-2021-07-04-12h26m28s639.png"
        )

        if day:
            str_builder = [
                "Ahem, ahem. Wakey, wakey! The sun is shining and everything is ",
                "beautiful. It is 8 AM and now officially daytime. Wake up, ",
                "get up, and get out there to greet another exciting day!",
            ]
        else:
            str_builder = [
                "Helloooo...? Helloooo? This is an important announcement. ",
                "Can't you see? It's 10 PM, and the moon's already out. ",
                "As such, it is officially nighttime. Sweet dreams, everyone! ",
                "Good night, sleep tight... You never know what creatures are out ",
                "in the jungle~",
            ]
        embed.description = "".join(str_builder)
        return embed

    @commands.slash_command(
        name="run-night-announcement",
        description="Runs the nighttime announcement automatically.",
        guild_ids=[673355251583025192],
        default_permission=False,
    )
    @commands.guild_permissions(673355251583025192, roles=utils.ADMIN_PERMS)
    async def run_night_announcement(self, inter: disnake.GuildCommandInteraction):
        await self.webhook.send(embed=self.gen_embed(day=False))
        await inter.send("Done!")

    @commands.slash_command(
        name="run-day-announcement",
        description="Runs the daytime announcement automatically.",
        guild_ids=[673355251583025192],
        default_permission=False,
    )
    @commands.guild_permissions(673355251583025192, roles=utils.ADMIN_PERMS)
    async def run_day_announcement(self, inter: disnake.GuildCommandInteraction):
        await self.webhook.send(embed=self.gen_embed(day=True))
        await inter.send("Done!")

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

            await disnake.utils.sleep_until(sleep_till)
            et_now = datetime.datetime.now(et)

            embed = self.gen_embed(day=bool(et_now.hour < 12))
            await self.webhook.send(embed=embed)
            await asyncio.sleep(3600)


def setup(bot):
    importlib.reload(utils)
    bot.add_cog(AutoAnnouncements(bot))
