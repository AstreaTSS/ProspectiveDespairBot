#!/usr/bin/env python3.8
import datetime
import importlib

import disnake
from disnake.ext import commands

import common.utils as utils


class OnCMDError(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error):
        # sourcery skip: remove-pass-elif
        if not ctx.bot.is_ready():
            return

        if isinstance(error, commands.CommandInvokeError):
            original = error.original
            if not isinstance(original, disnake.HTTPException):
                await utils.error_handle(self.bot, error, ctx)
        elif isinstance(error, commands.TooManyArguments):
            await ctx.reply(
                embed=utils.error_embed_generate(
                    "You passed too many arguments to that command! Please make sure"
                    " you're passing in a valid argument/subcommand."
                )
            )
        elif isinstance(error, commands.CommandOnCooldown):
            till = disnake.utils.utcnow() + datetime.timedelta(
                seconds=error.retry_after
            )
            await ctx.reply(
                embed=utils.error_embed_generate(
                    "You're doing that command too fast! "
                    + f"Try again {disnake.utils.format_dt(till, style='R')}."
                )
            )
        elif isinstance(
            error,
            (commands.ConversionError, commands.UserInputError, commands.BadArgument),
        ):
            await ctx.reply(embed=utils.error_embed_generate(str(error)))
        elif isinstance(error, utils.CustomCheckFailure):
            await ctx.reply(embed=utils.error_embed_generate(str(error)))
        elif isinstance(error, commands.CheckFailure):
            if ctx.guild:
                await ctx.reply(
                    embed=utils.error_embed_generate(
                        "You do not have the proper permissions to use that command."
                    )
                )
        elif isinstance(error, commands.CommandNotFound):
            pass
        else:
            await utils.error_handle(self.bot, error, ctx)

    @commands.Cog.listener()
    async def on_slash_command_error(
        self, inter: disnake.GuildCommandInteraction, error: commands.CommandError
    ):
        if isinstance(error, commands.BadArgument):
            await inter.send(
                embed=utils.error_embed_generate(str(error)), ephemeral=True
            )
        elif "Unknown interaction" in str(error):
            await inter.channel.send(
                f"{inter.author.mention}, the bot is a bit slow and so cannot do slash"
                " commands right now. Please wait a bit and try again.",
                delete_after=3,
            )
        else:
            await utils.error_handle(self.bot, error, inter)


def setup(bot):
    importlib.reload(utils)
    bot.add_cog(OnCMDError(bot))
