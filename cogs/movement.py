import collections
import importlib
import typing
import unicodedata

import disnake
from disnake.ext import commands

import common.fuzzys as fuzzys
import common.models as models
import common.paginator as paginator
import common.utils as utils


DORM_LINK_CHAN_ID = 938607273486471209


async def move_autocomplete(inter: disnake.CommandInteraction, argument: str):
    if isinstance(inter.channel, disnake.Thread):
        chan_id = inter.channel.parent_id
    else:
        chan_id = inter.channel.id

    channel_entries = await models.MovementEntry.filter(
        entry_channel_id=chan_id, user_id__in=[inter.user.id, None]
    )
    if not channel_entries:
        return {}

    channels = tuple(
        inter.guild.get_channel(c.dest_channel_id) for c in channel_entries
    )
    channels = tuple(c for c in channels if c is not None)

    if not argument:
        return {f"#{c.name}": c.id for c in channels}

    def get_channel_name(channel: disnake.TextChannel):
        return (
            channel.name.lower()
            if isinstance(channel, disnake.abc.GuildChannel)
            else channel
        )

    queried_channels: list[list[disnake.TextChannel]] = fuzzys.extract_from_list(
        inter=inter,
        argument=argument.lower(),
        list_of_items=channels,
        processors=[get_channel_name],
        score_cutoff=0,
    )
    return {f"#{c[0].name}": c[0].id for c in queried_channels}


async def move_check(inter: disnake.ApplicationCommandInteraction):
    return inter.bot.allowed_to_move and (
        inter.channel.category_id
        and inter.channel.category_id in {938606024523387000, 938606098204749914}
    )


class Movement(commands.Cog, name="Mini-KG Movement"):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

        guild = self.bot.get_guild(786609181855318047)
        self.participant_role: disnake.Role = guild.get_role(939993631140495360)  # type: ignore
        self.dorm_category: disnake.CategoryChannel = guild.get_channel(938606098204749914)  # type: ignore
        self.dorm_link_chan: disnake.TextChannel = guild.get_channel(DORM_LINK_CHAN_ID)  # type: ignore

    deny = disnake.PermissionOverwrite(
        view_channel=False, send_messages=False, send_messages_in_threads=False
    )
    allow = disnake.PermissionOverwrite(
        view_channel=True, send_messages=True, send_messages_in_threads=True
    )

    async def _move(
        self,
        member: disnake.Member,
        inter: disnake.GuildCommandInteraction,
        dest_channel: disnake.TextChannel,
    ):
        entry_channel = inter.channel
        if isinstance(entry_channel, disnake.Thread):
            entry_channel = entry_channel.parent

        await entry_channel.set_permissions(member, overwrite=self.deny)
        await entry_channel.send(
            f"{member.mention} left to `{dest_channel.name}.`",
            allowed_mentions=disnake.AllowedMentions.none(),
        )

        await dest_channel.set_permissions(member, overwrite=self.allow)
        await dest_channel.send(
            f"{member.mention} entered from `{entry_channel.name}.`",
            allowed_mentions=disnake.AllowedMentions.none(),
        )

    async def _create_links(
        self,
        entry_channel: disnake.TextChannel,
        dest_channel: disnake.TextChannel,
        member: typing.Optional[disnake.Member],
    ):
        await models.MovementEntry.create(
            entry_channel_id=entry_channel.id,
            dest_channel_id=dest_channel.id,
            user_id=member.id if member else None,
        )
        await models.MovementEntry.create(
            entry_channel_id=dest_channel.id,
            dest_channel_id=entry_channel.id,
            user_id=member.id if member else None,
        )

    @commands.slash_command(
        name="move",
        description="Allows you to move around in the Mini-KG.",
        guild_ids=[786609181855318047],
        default_permission=False,
    )
    @commands.guild_permissions(786609181855318047, roles=utils.MINI_KG_PERMS)
    @commands.check(move_check)  # type: ignore
    async def move(
        self,
        inter: disnake.GuildCommandInteraction,
        channel_id: int = commands.Param(
            name="channel",
            description="The channel to move to.",
            autocomplete=move_autocomplete,
        ),
    ):
        dest_channel = inter.guild.get_channel(channel_id)
        await inter.send("Sending...", ephemeral=True)
        await self._move(inter.user, inter, dest_channel)

    @commands.slash_command(
        name="allowed-to-move",
        description="Should people be allowed to move around the channels?",
        guild_ids=[786609181855318047],
        default_permission=False,
    )
    @commands.guild_permissions(786609181855318047, roles=utils.ADMIN_PERMS)
    async def allowed_to_move(
        self,
        inter: disnake.GuildCommandInteraction,
        allowed: bool = commands.Param(
            description="Should people be around to move around?"
        ),
    ):
        inter.bot.allowed_to_move = allowed
        await inter.send("Done!")

    @commands.slash_command(
        name="mass-move",
        description="Moves everyone in the game to one channel.",
        guild_ids=[786609181855318047],
        default_permission=False,
    )
    @commands.guild_permissions(786609181855318047, roles=utils.ADMIN_PERMS)
    async def mass_move(
        self,
        inter: disnake.GuildCommandInteraction,
        channel: disnake.TextChannel = commands.Param(
            description="The channel to move everyone to."
        ),
    ):
        await inter.response.defer(ephemeral=True)

        for member in self.participant_role.members:
            await self._move(member, inter, channel)

        await inter.send("Done!", ephemeral=True)

    @commands.slash_command(
        name="link-channels",
        description="Link channels for movement.",
        guild_ids=[786609181855318047],
        default_permission=False,
    )
    @commands.guild_permissions(786609181855318047, roles=utils.ADMIN_PERMS)
    async def link_channels(
        self,
        inter: disnake.GuildCommandInteraction,
        entry_channel: disnake.TextChannel = commands.Param(
            description="The starting channel."
        ),
        dest_channel: disnake.TextChannel = commands.Param(
            description="The exit channel."
        ),
        user: disnake.Member = commands.Param(
            None, description="The user to link this for, if desired."
        ),
    ):
        await inter.response.defer()

        exists = await models.MovementEntry.exists(
            entry_channel_id__in=[entry_channel.id, dest_channel.id],
            dest_channel_id__in=[dest_channel.id, entry_channel.id],
            user_id=user.id if user else None,
        )

        if not exists:
            await self._create_links(entry_channel, dest_channel, user)
            await inter.send("Done!")
        else:
            await inter.send("This entry already exists!")

    @commands.slash_command(
        name="unlink-channels",
        description="Unlinks channels for movement.",
        guild_ids=[786609181855318047],
        default_permission=False,
    )
    @commands.guild_permissions(786609181855318047, roles=utils.ADMIN_PERMS)
    async def unlink_channels(
        self,
        inter: disnake.GuildCommandInteraction,
        entry_channel: disnake.TextChannel = commands.Param(
            description="The starting channel."
        ),
        dest_channel: disnake.TextChannel = commands.Param(
            description="The exit channel."
        ),
        user: disnake.Member = commands.Param(
            None, description="The user to unlink this for, if specified."
        ),
    ):
        await inter.response.defer()

        num_deleted = await models.MovementEntry.filter(
            entry_channel_id__in=[entry_channel.id, dest_channel.id],
            dest_channel_id__in=[dest_channel.id, entry_channel.id],
            user_id=user.id if user else None,
        ).delete()

        if num_deleted > 0:
            await inter.send("Done!")
        else:
            await inter.send("This entry doesn't exist!")

    @commands.slash_command(
        name="dorm-generation",
        description="Generates dorms for all participants.",
        guild_ids=[786609181855318047],
        default_permission=False,
    )
    @commands.guild_permissions(786609181855318047, roles=utils.ADMIN_PERMS)
    async def dorm_generation(self, inter: disnake.GuildCommandInteraction):
        await inter.response.defer()

        dorm_category: disnake.CategoryChannel = inter.guild.get_channel(938606098204749914)  # type: ignore

        for channel in dorm_category.text_channels:
            await channel.delete()

        for member in self.participant_role.members:
            # this first line is more or less black magic, but it basically translates characters like 𝓭𝓼𝓰𝓼𝓭𝓰
            # into dsgsdg, which is easier to type
            # source - https://github.com/daveoncode/python-string-utils/blob/78929d/string_utils/manipulation.py#L433
            ascii_name = (
                unicodedata.normalize("NFKD", member.name.lower())
                .encode("ascii", "ignore")
                .decode("utc-8")
            )

            # then this is basically a bunch of basic conversion notes to make the process easier
            # not perfect, but the api can take it from here, i think
            somewhat_valid_name = (
                ascii_name.replace(" ", "-")
                .replace('"', "")
                .replace("'", "")
                .replace(".", "")
            )

            chan = await dorm_category.create_text_channel(
                name=f"{somewhat_valid_name}-{member.discriminator}-dorm"
            )
            await self._create_links(chan, self.dorm_link_chan, member)

        await inter.send("Done!")

    @commands.slash_command(
        name="view-links",
        description="Views the link for channels.",
        guild_ids=[786609181855318047],
        default_permission=False,
    )
    @commands.guild_permissions(786609181855318047, roles=utils.ADMIN_PERMS)
    async def view_links(
        self,
        inter: disnake.GuildCommandInteraction,
        entry_channel: disnake.TextChannel = commands.Param(
            None, description="The entry channel to view."
        ),
    ):
        await inter.response.defer()

        if entry_channel:
            channel_entries = await models.MovementEntry.filter(
                entry_channel_id=entry_channel.id,
            )

            chan_entry_strs = [
                f"<#{e.dest_channel_id}> {f'(<@{e.user_id}>)' if e.user_id else ''}"
                for e in channel_entries
            ]

            if not chan_entry_strs:
                await inter.send("There's no links for this channel!")

            chan_entry_embed = disnake.Embed(
                color=self.bot.color,
                title=f"Destination channels for #{entry_channel.name}",
                description="\n".join(chan_entry_strs),
            )
            await inter.send(embed=chan_entry_embed)
        else:
            channel_dict: typing.DefaultDict[
                int, typing.List[models.MovementEntry]
            ] = collections.defaultdict(list)

            async for channel_entry in models.MovementEntry.all():
                channel_dict[channel_entry.entry_channel_id].append(channel_entry)

            channel_pages_dicts: typing.List[typing.Dict[str, str]] = []

            for channel_id, channel_entries in channel_dict.items():
                chan_entry_strs = [
                    f"<#{e.dest_channel_id}> {f'(<@{e.user_id}>)' if e.user_id else ''}"
                    for e in channel_entries
                ]
                entry_chan = inter.guild.get_channel(channel_id)
                channel_pages_dicts.append(
                    {
                        f"Destination channels for #{entry_chan.name}": "\n".join(
                            chan_entry_strs
                        )
                    }
                )

            channel_paginator = paginator.FieldPages(
                inter, entries=channel_pages_dicts, per_page=1
            )
            await channel_paginator.paginate()


def setup(bot: commands.Bot):
    importlib.reload(utils)
    importlib.reload(fuzzys)
    importlib.reload(paginator)
    bot.add_cog(Movement(bot))
