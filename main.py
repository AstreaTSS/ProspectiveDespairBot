import asyncio
import logging
import os

import discord
import dislash
from discord.ext import commands
from dotenv import load_dotenv
from tortoise import Tortoise
from websockets import ConnectionClosedOK

import common.utils as utils
import keep_alive
from common.help_cmd import PaginatedHelpCommand


load_dotenv()

logger = logging.getLogger("discord")
logger.setLevel(logging.INFO)
handler = logging.FileHandler(
    filename=os.environ.get("LOG_FILE_PATH"), encoding="utf-8", mode="a"
)
handler.setFormatter(
    logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s")
)
logger.addHandler(handler)


async def pd_prefixes(bot: commands.Bot, msg: discord.Message):
    mention_prefixes = {f"{bot.user.mention} ", f"<@!{bot.user.id}> "}
    custom_prefixes = {"p!"}
    return mention_prefixes.union(custom_prefixes)


def global_checks(ctx: commands.Context):
    if not ctx.bot.is_ready():
        return False

    if ctx.bot.init_load:
        return False

    if not ctx.guild:
        return False

    return ctx.guild.id == 786609181855318047 or ctx.author.id == ctx.bot.owner.id


async def on_init_load():
    await bot.wait_until_ready()

    await Tortoise.init(
        db_url=os.environ.get("DB_URL"), modules={"models": ["common.models"]}
    )

    application = await bot.application_info()
    bot.owner = application.owner

    bot.load_extension("jishaku")

    cogs_list = utils.get_all_extensions(os.environ.get("DIRECTORY_OF_FILE"))

    for cog in cogs_list:
        try:
            bot.load_extension(cog)
        except commands.NoEntryPointError as e:
            pass

    bot.init_load = False


class ProspectiveDespairBot(commands.Bot):
    def __init__(
        self,
        command_prefix,
        help_command=PaginatedHelpCommand(),
        description=None,
        **options,
    ):
        super().__init__(
            command_prefix,
            help_command=help_command,
            description=description,
            **options,
        )
        self._checks.append(global_checks)

    async def on_ready(self):
        utcnow = discord.utils.utcnow()
        time_format = discord.utils.format_dt(utcnow)

        connect_msg = (
            f"Logged in at {time_format}!"
            if self.init_load == True
            else f"Reconnected at {time_format}!"
        )

        while not hasattr(self, "owner"):
            await asyncio.sleep(0.1)

        await self.owner.send(connect_msg)

        activity = discord.Activity(
            name="over Prospective Despair", type=discord.ActivityType.watching
        )

        try:
            await self.change_presence(activity=activity)
        except ConnectionClosedOK:
            await utils.msg_to_owner(self, "Reconnecting...")

    async def on_resumed(self):
        activity = discord.Activity(
            name="over Prospective Despair", type=discord.ActivityType.watching
        )
        await self.change_presence(activity=activity)

    async def on_error(self, event, *args, **kwargs):
        try:
            raise
        except BaseException as e:
            await utils.error_handle(self, e)

    async def get_context(self, message, *, cls=commands.Context):
        """A simple extension of get_content. If it doesn't manage to get a command, it changes the string used
        to get the command from - to _ and retries. Convenient for the end user."""

        ctx = await super().get_context(message, cls=cls)
        if ctx.command is None and ctx.invoked_with:
            ctx.command = self.all_commands.get(ctx.invoked_with.replace("-", "_"))

        return ctx

    async def close(self):
        await Tortoise.close_connections()  # this will complain a bit, just ignore it
        return await super().close()


intents = discord.Intents.all()
mentions = discord.AllowedMentions.all()

bot = ProspectiveDespairBot(
    command_prefix=pd_prefixes, allowed_mentions=mentions, intents=intents,
)
slash = dislash.InteractionClient(bot, modify_send=False)

bot.init_load = True
bot.color = discord.Color(int(os.environ.get("BOT_COLOR")))  # 2ebae1, aka 3062497

bot.loop.create_task(on_init_load())
keep_alive.keep_alive()
bot.run(os.environ.get("MAIN_TOKEN"))
