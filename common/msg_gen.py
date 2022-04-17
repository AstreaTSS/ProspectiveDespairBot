#!/usr/bin/env python3.8
import collections
import os
import re
import typing

import aiohttp
import disnake
from disnake.ext import commands

import common.utils as utils

# this is an ugly mess of functions thrown in here from seraphim


async def type_from_url(url):
    # gets type of data from url
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                return None

            data = await resp.content.read(12)
            tup_data = tuple(data)

            # first 7 bytes of most pngs
            png_list = (0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A)
            if tup_data[:8] == png_list:
                return "png"

            # fmt: off
            # first 12 bytes of most jp(e)gs. EXIF is a bit wierd, and so some manipulating has to be done
            jfif_list = (0xFF, 0xD8, 0xFF, 0xE0, 0x00, 0x10, 0x4A, 0x46,
                0x49, 0x46, 0x00, 0x01)
            # fmt: on
            exif_lists = (
                (0xFF, 0xD8, 0xFF, 0xE1),
                (0x45, 0x78, 0x69, 0x66, 0x00, 0x00),
            )

            if tup_data == jfif_list or (
                tup_data[:4] == exif_lists[0] and tup_data[6:] == exif_lists[1]
            ):
                return "jpg"

            # first 3 bytes of some jp(e)gs.
            weird_jpeg_list = (0xFF, 0xD8, 0xFF)
            if tup_data[:3] == weird_jpeg_list:
                return "jpg"

            # copied from d.py's _get_mime_type_for_image
            if tup_data[:3] == b"\xff\xd8\xff" or tup_data[6:10] in (b"JFIF", b"Exif"):
                return "jpg"

            # first 6 bytes of most gifs. last two can be different, so we have to handle that
            gif_lists = ((0x47, 0x49, 0x46, 0x38), ((0x37, 0x61), (0x39, 0x61)))
            if tup_data[:4] == gif_lists[0] and tup_data[4:6] in gif_lists[1]:
                return "gif"

            # first 12 bytes of most webps. middle four are file size, so we ignore that
            webp_lists = ((0x52, 0x49, 0x46, 0x46), (0x57, 0x45, 0x42, 0x50))
            if tup_data[:4] == webp_lists[0] and tup_data[8:] == webp_lists[1]:
                return "webp"

    return None


async def tenor_handle(url: str):
    # handles getting gifs from tenor links
    dash_split = url.split("-")

    params = {
        "ids": dash_split[-1],
        "key": os.environ.get("TENOR_KEY"),
        "media_filter": "minimal",
    }

    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.tenor.com/v1/gifs", params=params) as resp:
            resp_json = await resp.json()

            try:
                return resp_json["results"][0]["media"][0]["gif"]["url"]
            except (KeyError, IndexError):
                return None


async def get_image_url(url: str):
    # handles getting true image url from a url

    if "https://tenor.com/view" in url or "http://tenor.com/view" in url:
        gif_url = await tenor_handle(url)
        if gif_url != None:
            return gif_url

    else:
        try:
            file_type = await type_from_url(url)
        except aiohttp.InvalidURL:
            return None

        image_endings = ("jpg", "jpeg", "png", "gif", "webp")
        image_extensions = tuple(image_endings)  # no idea why I have to do this

        if file_type in image_extensions:
            return url

    return None


def get_content(message: disnake.Message):  # sourcery no-metrics
    """Because system_content isn't perfect.
    More or less a copy of system_content with name being swapped with \
    display_name and DM message types removed."""

    if message.type is disnake.MessageType.default:
        return message.content

    if message.type is disnake.MessageType.recipient_add:
        return (
            f"{message.author.display_name} added {message.mentions[0].name} to the"
            " thread."
        )

    if message.type is disnake.MessageType.recipient_remove:
        return (
            f"{message.author.display_name} removed {message.mentions[0].name} from the"
            " thread."
        )

    if message.type is disnake.MessageType.channel_name_change:
        return (
            f"{message.author.display_name} changed the channel name:"
            f" **{message.content}**"
        )

    if message.type is disnake.MessageType.pins_add:
        return f"{message.author.display_name} pinned a message to this channel."

    if message.type is disnake.MessageType.new_member:
        formats = [
            "{0} joined the party.",
            "{0} is here.",
            "Welcome, {0}. We hope you brought pizza.",
            "A wild {0} appeared.",
            "{0} just landed.",
            "{0} just slid into the server.",
            "{0} just showed up!",
            "Welcome {0}. Say hi!",
            "{0} hopped into the server.",
            "Everyone welcome {0}!",
            "Glad you're here, {0}.",
            "Good to see you, {0}.",
            "Yay you made it, {0}!",
        ]

        created_at_ms = int(message.created_at.timestamp() * 1000)
        return formats[created_at_ms % len(formats)].format(message.author.display_name)

    if message.type is disnake.MessageType.premium_guild_subscription:
        if not message.content:
            return f"**{message.author.display_name}** just boosted the server!"
        else:
            return (
                f"**{message.author.display_name}** just boosted the"
                f" server **{message.content}** times!"
            )

    if message.type is disnake.MessageType.premium_guild_tier_1:
        if not message.content:
            return (
                f"**{message.author.display_name}** just boosted the"
                f" server! {message.guild} has achieved **Level 1!**"
            )
        else:
            return (
                f"**{message.author.display_name}** just boosted the"
                f" server **{message.content}** times! {message.guild} has achieved"
                " **Level 1!**"
            )

    if message.type is disnake.MessageType.premium_guild_tier_2:
        if not message.content:
            return (
                f"**{message.author.display_name}** just boosted the"
                f" server! {message.guild} has achieved **Level 2!**"
            )
        else:
            return (
                f"**{message.author.display_name}** just boosted the"
                f" server **{message.content}** times! {message.guild} has achieved"
                " **Level 2!**"
            )

    if message.type is disnake.MessageType.premium_guild_tier_3:
        if not message.content:
            return (
                f"**{message.author.display_name}** just boosted the"
                f" server! {message.guild} has achieved **Level 3!**"
            )
        else:
            return (
                f"**{message.author.display_name}** just boosted the"
                f" server **{message.content}** times! {message.guild} has achieved"
                " **Level 3!**"
            )

    if message.type is disnake.MessageType.channel_follow_add:
        return (
            f"{message.author.display_name} has added {message.content} to this channel"
        )

    if message.type is disnake.MessageType.guild_stream:
        return (
            f"{message.author.display_name} is live! Now streaming"
            f" {message.author.activity.name}"  # type: ignore
        )

    if message.type is disnake.MessageType.guild_discovery_disqualified:
        return (
            "This server has been removed from Server Discovery because it no longer"
            " passes all the requirements. Check Server Settings for more details."
        )

    if message.type is disnake.MessageType.guild_discovery_requalified:
        return (
            "This server is eligible for Server Discovery again and has been"
            " automatically relisted!"
        )

    if message.type is disnake.MessageType.guild_discovery_grace_period_initial_warning:
        return (
            "This server has failed Discovery activity requirements for 1 week. If this"
            " server fails for 4 weeks in a row, it will be automatically removed from"
            " Discovery."
        )

    if message.type is disnake.MessageType.guild_discovery_grace_period_final_warning:
        return (
            "This server has failed Discovery activity requirements for 3 weeks in a"
            " row. If this server fails for 1 more week, it will be removed from"
            " Discovery."
        )

    if message.type is disnake.MessageType.thread_created:
        return (
            f"{message.author.display_name} started a thread: **{message.content}**."
            " See all **threads**."
        )

    if message.type is disnake.MessageType.reply:
        return message.content

    if message.type is disnake.MessageType.thread_starter_message:
        if message.reference is None or message.reference.resolved is None:
            return "Sorry, we couldn't load the first message in this thread"

        return message.reference.resolved.content  # type: ignore

    if message.type is disnake.MessageType.guild_invite_reminder:
        return (
            "Wondering who to invite?\nStart by inviting anyone who can help you build"
            " the server!"
        )

    raise TypeError(f"Invalid MessageType: {message.type}!")


async def user_from_id(bot, guild, user_id):
    if user_id is None:
        return None

    # gets a user from id. attempts via guild first, then attempts globally
    user = guild.get_member(user_id)  # member in guild
    if user is None:
        user = bot.get_user(user_id)  # user in cache

    if user is None:
        try:
            user = await bot.fetch_user(user_id)  # a user that exists
        except disnake.NotFound:
            user = None

    return user


async def resolve_reply(
    bot: commands.Bot, msg: disnake.Message
) -> typing.Optional[disnake.Message]:
    reply: typing.Optional[disnake.Message] = None

    if msg.reference:
        if (
            msg.reference.resolved
            and isinstance(msg.reference.resolved, disnake.Message)
        ) or msg.reference.cached_message:
            # saves time fetching messages if possible
            reply = (
                msg.reference.cached_message or msg.reference.resolved  # type: ignore
            )
        elif guild := bot.get_guild(msg.reference.guild_id):  # type: ignore
            chan = guild.get_channel_or_thread(msg.reference.channel_id)  # type: ignore
            try:
                reply = await chan.fetch_message(msg.reference.message_id)  # type: ignore
            except disnake.HTTPException or AttributeError:
                pass

    return reply


def get_author_id(mes: disnake.Message, bot: commands.Bot):
    # gets author id from message
    author_id = None
    if (
        mes.author.id == 700857077672706120
        and mes.embeds != []
        and mes.embeds[0].type == "rich"
        and mes.embeds[0].author.name != bot.user.name
        and isinstance(mes.embeds[0].author.icon_url, str)
        and "&userid=" in mes.embeds[0].author.icon_url
    ):
        # conditions to check if message = sniped message from Seraphim
        # not perfect by any means, but it works for general use

        try:
            return int(mes.embeds[0].author.icon_url.split("&userid=")[1])
        except ValueError:
            return mes.author.id
    else:
        author_id = mes.author.id

    return author_id


def cant_display(embed: disnake.Embed, attachments: list, index=0):
    attach_strs = collections.deque()

    for x in range(len(attachments)):
        if x < index:
            continue

        attachment = attachments[x]
        if attachment.is_spoiler():
            attach_strs.append(f"||[{attachment.filename}]({attachment.url})||")
        else:
            attach_strs.append(f"[{attachment.filename}]({attachment.url})")

    if index == 0:
        embed.add_field(name="Attachments", value="\n".join(attach_strs), inline=False)
    else:
        embed.add_field(
            name="Other Attachments", value="\n".join(attach_strs), inline=False
        )

    return embed


async def base_generate(
    bot: commands.Bot, mes: disnake.Message, no_attachments: bool = False
):
    # sourcery no-metrics
    # generates core of star messages
    image_url = ""

    if (
        mes.embeds
        and mes.author.id == 700857077672706120
        and mes.embeds[0].author.name != bot.user.name
        and mes.embeds[0].fields != disnake.Embed.Empty
        and mes.embeds[0].footer.text != disnake.Embed.Empty
        and mes.embeds[0].footer.text.startswith("ID:")
    ):  # all of this... for pinboard support
        send_embed = mes.embeds[
            0
        ].copy()  # it's using the same internal gen, so why not just copy it

        for x in range(len(send_embed.fields)):
            if send_embed.fields[x].name == "Original":
                send_embed.remove_field(x)
                break

        # next pieces of code make the embed more how a normally generated embed would be like
        send_embed.color = bot.color
        send_embed.timestamp = mes.created_at
        send_embed.set_footer()  # will set footer to default, aka none

    elif (
        mes.embeds != []
        and mes.embeds[0].type == "rich"
        and mes.author.id == 700857077672706120
        and isinstance(mes.embeds[0].author.icon_url, str)
        and "&userid=" in mes.embeds[0].author.icon_url
    ):  # if message is sniped message that's supported
        snipe_embed = mes.embeds[0]

        author_id = get_author_id(mes, bot)
        author = await user_from_id(bot, mes.guild, author_id)

        author_str = ""
        if author is None or author.id == 700857077672706120:
            author_str = mes.embeds[0].author.name
        else:
            author_str = f"{author.display_name} ({author})"

        icon = (
            snipe_embed.author.icon_url
            if author is None or author.id == 700857077672706120
            else utils.get_icon_url(author.display_avatar)
        )

        content = snipe_embed.description

        send_embed = disnake.Embed(
            title="Sniped:",
            colour=bot.color,
            description=content,
            timestamp=mes.created_at,
        )
        send_embed.set_author(name=author_str, icon_url=icon)

    elif (
        mes.author.bot
        and mes.embeds != []
        and mes.embeds[0].description != disnake.Embed.Empty
        and mes.embeds[0].type == "rich"
        and (
            mes.embeds[0].footer.icon_url
            != "https://abs.twimg.com/icons/apple-touch-icon-192x192.png"
            and mes.embeds[0].footer.text != "Twitter"
        )
    ):

        author = f"{mes.author.display_name} ({mes.author})"
        icon = utils.get_icon_url(mes.author.display_avatar)

        send_embed = disnake.Embed(
            colour=bot.color,
            description=mes.embeds[0].description,
            timestamp=mes.created_at,
        )
        send_embed.set_author(name=author, icon_url=icon)

    else:
        content = get_content(mes)
        author = f"{mes.author.display_name} ({mes.author})"
        icon = utils.get_icon_url(mes.author.display_avatar)

        if content:
            send_embed = disnake.Embed(
                colour=bot.color,
                description=content,
                timestamp=mes.created_at,
            )
        else:
            send_embed = disnake.Embed(
                colour=bot.color,
                description=disnake.Embed.Empty,
                timestamp=mes.created_at,
            )
        send_embed.set_author(name=author, icon_url=icon)

        if mes.type == disnake.MessageType.reply:
            # checks if message has inline reply

            ref_mes_url = mes.reference.jump_url  # type: ignore

            reply_msg = await resolve_reply(bot, mes)
            ref_author = reply_msg.author if reply_msg else None
            ref_auth_str = ref_author.display_name if ref_author else "a message"

            send_embed.title = f"Replying to {ref_auth_str}:"
            send_embed.url = ref_mes_url

        if (
            mes.embeds != []
            and mes.embeds[0].type == "image"
            and mes.embeds[0].thumbnail.url != disnake.Embed.Empty
        ):
            image_url = mes.embeds[0].thumbnail.url

            if not no_attachments and mes.attachments:
                send_embed = cant_display(send_embed, mes.attachments, 0)
        elif not no_attachments and mes.attachments != []:
            if (
                mes.attachments[0]
                .proxy_url.lower()
                .endswith(("jpg", "jpeg", "png", "gif", "webp"))
                and not mes.attachments[0].is_spoiler()
            ):
                image_url = mes.attachments[0].proxy_url

                if len(mes.attachments) > 1:
                    send_embed = cant_display(send_embed, mes.attachments, 1)
            else:
                send_embed = cant_display(send_embed, mes.attachments, 0)
        else:
            if not mes.flags.suppress_embeds:  # would suppress images too
                # http://urlregex.com/
                urls = re.findall(
                    r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",
                    content,
                )
                if urls != []:
                    first_url = urls[0]

                    possible_url = await get_image_url(first_url)
                    if possible_url != None:
                        image_url = possible_url

                # if the image url is still blank and the message has a gifv embed
                if (
                    image_url == ""
                    and mes.embeds != []
                    and mes.embeds[0].type == "gifv"
                ) and (
                    mes.embeds[0].thumbnail.url != disnake.Embed.Empty
                ):  # if there is a thumbnail url
                    image_url = mes.embeds[0].thumbnail.url

                # if the image url is STILL blank and there's a youtube video
                if (
                    image_url == ""
                    and mes.embeds
                    and mes.embeds[0].type == "video"
                    and mes.embeds[0].provider != disnake.Embed.Empty
                    and mes.embeds[0].provider.name != disnake.Embed.Empty
                    and mes.embeds[0].provider.name == "YouTube"
                ):
                    image_url = mes.embeds[0].thumbnail.url
                    send_embed.add_field(
                        name="YouTube:",
                        value=(
                            f"{mes.embeds[0].author.name}:"
                            f" [{mes.embeds[0].title}]({mes.embeds[0].url})"
                        ),
                        inline=False,
                    )

            # if the image url is STILL blank and the message has a sticker
            if image_url == "" and mes.stickers:
                if mes.stickers[0].format != disnake.StickerFormatType.lottie:
                    image_url = str(mes.stickers[0].url)
                else:  # as of right now, you cannot send content with a sticker, so we might as well
                    send_embed.description = (
                        "*This message has a sticker that I cannot display.*"
                    )

            if not no_attachments and mes.attachments:
                send_embed = cant_display(send_embed, mes.attachments, 0)

    if image_url != "":
        send_embed.set_image(url=image_url)

    return send_embed
