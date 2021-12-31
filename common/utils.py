#!/usr/bin/env python3.8
import collections
import logging
import traceback
import typing
from decimal import Decimal
from decimal import InvalidOperation
from pathlib import Path

import aiohttp
import disnake
from disnake.ext import commands


class DecimalConverter(commands.Converter):
    async def convert(self, ctx: commands.Context, argument: str) -> Decimal:
        try:
            return Decimal(argument)
        except InvalidOperation:
            raise commands.BadArgument("This is not a decimal!")


class CustomCheckFailure(commands.CheckFailure):
    # custom classs for custom prerequisite failures outside of normal command checks
    pass


async def error_handle(
    bot, error, ctx: typing.Union[commands.Context, disnake.Interaction, None] = None,
):
    # handles errors and sends them to owner
    if isinstance(error, aiohttp.ServerDisconnectedError):
        to_send = "Disconnected from server!"
        split = True
    else:
        error_str = error_format(error)
        logging.getLogger("disnake").error(error_str)

        error_split = error_str.splitlines()
        chunks = [error_split[x : x + 20] for x in range(0, len(error_split), 20)]
        for chunk_ in chunks:
            chunk_[0] = f"```py\n{chunk_[0]}"
            chunk_[len(chunk_) - 1] += "\n```"

        final_chunks = ["\n".join(chunk) for chunk in chunks]
        if ctx and hasattr(ctx, "message") and hasattr(ctx.message, "jump_url"):
            final_chunks.insert(0, f"Error on: {ctx.message.jump_url}")

        to_send = final_chunks
        split = False

    await msg_to_owner(bot, to_send, split)

    if ctx:
        if isinstance(ctx, commands.Context):
            await ctx.reply(
                "An internal error has occured. The bot owner has been notified."
            )
        else:
            await ctx.send(
                content="An internal error has occured. The bot owner has been notified.",
            )


async def msg_to_owner(bot, content, split=True):
    # sends a message to the owner
    owner = bot.owner
    string = str(content)

    str_chunks = string_split(string) if split else content
    for chunk in str_chunks:
        await owner.send(f"{chunk}")


def line_split(content: str, split_by=20):
    content_split = content.splitlines()
    return [
        content_split[x : x + split_by] for x in range(0, len(content_split), split_by)
    ]


def embed_check(embed: disnake.Embed) -> bool:
    """Checks if an embed is valid, as per Discord's guidelines.
    See https://discord.com/developers/docs/resources/channel#embed-limits for details."""
    if len(embed) > 6000:
        return False

    if embed.title and len(embed.title) > 256:
        return False
    if embed.description and len(embed.description) > 4096:
        return False
    if embed.author and embed.author.name and len(embed.author.name) > 256:
        return False
    if embed.footer and embed.footer.text and len(embed.footer.text) > 2048:
        return False
    if embed.fields:
        if len(embed.fields) > 25:
            return False
        for field in embed.fields:
            if field.name and len(field.name) > 1024:
                return False
            if field.value and len(field.value) > 2048:
                return False

    return True


def deny_mentions(user):
    # generates an AllowedMentions object that only pings the user specified
    return disnake.AllowedMentions(everyone=False, users=[user], roles=False)


def error_format(error):
    # simple function that formats an exception
    return "".join(
        traceback.format_exception(
            etype=type(error), value=error, tb=error.__traceback__
        )
    )


def string_split(string):
    # simple function that splits a string into 1950-character parts
    return [string[i : i + 1950] for i in range(0, len(string), 1950)]


def file_to_ext(str_path, base_path):
    # changes a file to an import-like string
    str_path = str_path.replace(base_path, "")
    str_path = str_path.replace("/", ".")
    return str_path.replace(".py", "")


def get_all_extensions(str_path, folder="cogs"):
    # gets all extensions in a folder
    ext_files = collections.deque()
    loc_split = str_path.split("cogs")
    base_path = loc_split[0]

    if base_path == str_path:
        base_path = base_path.replace("main.py", "")
    base_path = base_path.replace("\\", "/")

    if base_path[-1] != "/":
        base_path += "/"

    pathlist = Path(f"{base_path}/{folder}").glob("**/*.py")
    for path in pathlist:
        str_path = str(path.as_posix())
        str_path = file_to_ext(str_path, base_path)

        if str_path != "cogs.db_handler":
            ext_files.append(str_path)

    return ext_files


def toggle_friendly_str(bool_to_convert):
    if bool_to_convert == True:
        return "on"
    else:
        return "off"


def yesno_friendly_str(bool_to_convert):
    if bool_to_convert == True:
        return "yes"
    else:
        return "no"


def error_embed_generate(error_msg):
    return disnake.Embed(colour=disnake.Colour.red(), description=error_msg)


def generate_mentions(ctx: commands.Context):
    # sourcery skip: remove-unnecessary-else
    # generates an AllowedMentions object that is similar to what a user can usually use

    permissions = ctx.channel.permissions_for(ctx.author)
    can_mention = permissions.administrator or permissions.mention_everyone

    if can_mention:
        # i could use a default AllowedMentions object, but this is more clear
        return disnake.AllowedMentions(everyone=True, users=True, roles=True)
    else:
        pingable_roles = tuple(r for r in ctx.guild.roles if r.mentionable)
        return disnake.AllowedMentions(everyone=False, users=True, roles=pingable_roles)


def get_icon_url(asset: disnake.Asset, size=128):
    if asset.is_animated():
        return str(asset.replace(format="gif", size=size))
    else:
        return str(asset.replace(format="png", size=size))


def proper_permissions():
    async def predicate(ctx: commands.Context):
        # checks if author has admin or manage guild perms or is the owner
        permissions = ctx.channel.permissions_for(ctx.author)
        return permissions.administrator or permissions.manage_guild

    return commands.check(predicate)


def deprecated_cmd():
    async def predicate(ctx: commands.Context):
        await ctx.reply(
            embed=error_embed_generate(
                "This command is deprecated, "
                + "and will be removed in a later release. Please use "
                + f"`/{ctx.command.qualified_name.replace('_', '-')}`` instead."
            )
        )
        return True

    return commands.check(predicate)


ADMIN_PERMS = {786610218133094420: True, 229350299909881876: True}

ALIVE_PLAYER_PERMS = {
    786610218133094420: True,
    786610731826544670: True,
    229350299909881876: True,
}
