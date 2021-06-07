import datetime
import os
import importlib

import pytz
import discord
import aiohttp
from discord.ext import commands

import common.backport_task as backport_task
import common.utils as utils

et = pytz.timezone("US/Eastern")

class AutoAnnouncements(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.webhook = discord.Webhook.from_url(
            os.environ.get("WEBHOOK_URL"),
            adapter=discord.AsyncWebhookAdapter(
                aiohttp.ClientSession(loop=self.bot.loop)
            ),
        )

        self.auto_run.start()
        
    def cog_unload(self):
        self.auto_run.cancel()

    @backport_task.loop(time=(
        datetime.time(hour=9, tzinfo=et),
        datetime.time(hour=23, tzinfo=et)
    ))
    async def auto_run(self):
        embed = discord.Embed(title="Announcement from Drake Aelius", color=11779669)
        et_now = datetime.datetime.now(et)

        if et_now.hour == 23:
            embed.description = """It's 11 PM. Go to sleep.
            The mess hall will close in a few minutes. Move out of it quickly: it would be rather \
            pathetic if you died just by being in it.
                
            Remember: all you have to do to escape is kill... and I heard night time's the *perfect* time to kill."""
        else:
            embed.description = """Wake up, idiots.
            It's now 9 AM. Unless you're a lazy ass, you should probably get ready for the day. And yeah, the mess hall has been unlocked too.

            Remember: if you want to escape, all you have to do is kill. If you can't convince yourself to do that... how weak."""

        await self.webhook.send(embed=embed)

    @auto_run.error
    async def error_handle(self, *args):
        error = args[-1]
        await utils.error_handle(self.bot, error)


def setup(bot):
    importlib.reload(utils)
    importlib.reload(backport_task)
    bot.add_cog(AutoAnnouncements(bot))