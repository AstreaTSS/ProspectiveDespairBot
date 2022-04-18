import asyncio
import collections
import importlib
import io
import typing
import unicodedata

import chat_exporter
import disnake
from disnake.ext import commands
from tortoise.expressions import Q

import common.fuzzys as fuzzys
import common.models as models
import common.paginator as paginator
import common.utils as utils


DORM_LINK_CHAN_ID = 938607273486471209


async def allowed_to_move(inter: disnake.ApplicationCommandInteraction) -> bool:
    result: str = await inter.bot.redis.hget(
        f"{inter.bot.user.id}{inter.user.id}", "allowed_to_move"
    )
    return result == "T"


async def move_check(inter: disnake.ApplicationCommandInteraction):
    return await allowed_to_move(inter) and (
        inter.channel.category_id
        and inter.channel.category_id in {938606024523387000, 938606098204749914}
    )


async def move_autocomplete(
    inter: disnake.ApplicationCommandInteraction, argument: str
):
    can_move = await move_check(inter)
    if not can_move:
        return {}

    if isinstance(inter.channel, disnake.Thread):
        chan_id = inter.channel.parent_id
    else:
        chan_id = inter.channel.id

    channel_entries = await models.MovementEntry.filter(
        Q(entry_channel_id=chan_id)
        & (Q(user_id=inter.user.id) | Q(user_id__isnull=True))
    )
    if not channel_entries:
        return {}

    channels = tuple(
        inter.guild.get_channel(c.dest_channel_id) for c in channel_entries
    )
    channels = tuple(c for c in channels if c is not None)

    if not argument:
        return {f"#{c.name}": str(c.id) for c in channels}

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
        score_cutoff=60,
    )
    return {f"#{c[0].name}": str(c[0].id) for c in queried_channels}


class MiniKG(commands.Cog, name="Mini-KG"):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

        guild = self.bot.get_guild(786609181855318047)
        self.participant_role: disnake.Role = guild.get_role(939993631140495360)  # type: ignore
        self.signed_up_role: disnake.Role = guild.get_role(954196014322053170)  # type: ignore
        self.spectator_role: disnake.Role = guild.get_role(965405511354843166)  # type: ignore
        self.dorm_category: disnake.CategoryChannel = guild.get_channel(938606098204749914)  # type: ignore
        self.dorm_link_chan: disnake.TextChannel = guild.get_channel(DORM_LINK_CHAN_ID)  # type: ignore

    deny = disnake.PermissionOverwrite(
        view_channel=False,
        send_messages=False,
        read_message_history=False,
        send_messages_in_threads=False,
    )
    allow = disnake.PermissionOverwrite(
        view_channel=True,
        send_messages=True,
        read_message_history=False,
        send_messages_in_threads=True,
    )

    async def _detect_empty(self, channel: disnake.TextChannel):
        # this next line is dangerous, but the redis we use maybe has
        # a thousand keys at once. it is much faster than using a scan method
        # and is very unlikely to affect our db
        # that being said, switching to a scan in the future isn't exactly the
        # worst thing in the world.
        keys = await self.bot.redis.keys(f"{self.bot.user.id}*")
        for key in keys:
            channel_id = await self.bot.redis.hget(key, "current_channel")
            if str(channel.id) == channel_id:
                return

        # this lets the history viewer know we dont need anything
        # before this
        await channel.send("```\nEnd.\n```")

    async def _move(
        self,
        member: disnake.Member,
        inter: disnake.GuildCommandInteraction,
        dest_channel: disnake.TextChannel,
    ):
        entry_channel_id: typing.Optional[str] = await inter.bot.redis.hget(
            f"{inter.bot.user.id}{member.id}", "current_channel"
        )
        if entry_channel_id:
            entry_channel = inter.guild.get_channel(int(entry_channel_id))
            valid_category = entry_channel.category_id in {
                938606024523387000,
                938606098204749914,
            }
        else:
            entry_channel = None
            valid_category = False

        if valid_category:
            await entry_channel.set_permissions(member, overwrite=self.deny)
            await entry_channel.send(
                f"{member.mention} left to `#{dest_channel.name}`.",
                allowed_mentions=disnake.AllowedMentions.none(),
            )

        await dest_channel.set_permissions(member, overwrite=self.allow)
        await inter.bot.redis.hset(
            f"{inter.bot.user.id}{member.id}", "current_channel", str(dest_channel.id)
        )

        if entry_channel and valid_category:
            # this is a potentially somewhat long lasting function - its best if we
            # offload it like this
            asyncio.create_task(self._detect_empty(entry_channel))

        await asyncio.sleep(1)
        if valid_category:
            await dest_channel.send(
                f"{member.mention} entered from `#{entry_channel.name}`.",
                allowed_mentions=disnake.AllowedMentions.all(),
            )
        else:
            await dest_channel.send(
                f"{member.mention} entered `#{dest_channel.name}`.",
                allowed_mentions=disnake.AllowedMentions.all(),
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

    async def _create_move_select(
        self,
        inter: disnake.GuildCommandInteraction,
        member: disnake.Member,
    ):
        """Creates the select component."""
        ori_self = self

        if isinstance(inter.channel, disnake.Thread):
            chan_id = inter.channel.parent_id
        else:
            chan_id = inter.channel.id

        channel_entries = await models.MovementEntry.filter(
            Q(entry_channel_id=chan_id)
            & (Q(user_id=member.id) | Q(user_id__isnull=True))
        )

        if not channel_entries:
            return None

        channels = tuple(
            inter.guild.get_channel(c.dest_channel_id) for c in channel_entries
        )
        channels = tuple(c for c in channels if c is not None)

        options = [
            disnake.SelectOption(label=f"#{c.name}", value=f"pdminimove:{c.id}")
            for c in channels
        ]

        class Dropdown(disnake.ui.Select):
            def __init__(self):
                super().__init__(
                    min_values=1,
                    max_values=1,
                    options=options,
                )

            async def callback(self, inter: disnake.Interaction):
                await inter.response.defer(ephemeral=True)

                channel_id = int(self.values[0].replace("pdminimove:", ""))
                channel = inter.guild.get_channel(channel_id)

                await ori_self._move(member, inter, channel)

        class DropdownView(disnake.ui.View):
            def __init__(self):
                super().__init__()
                self.add_item(Dropdown())

            async def interaction_check(self, interaction: disnake.Interaction) -> bool:
                return interaction.user.id == member.id

            async def on_error(
                self, error: Exception, _, inter: disnake.MessageInteraction
            ) -> None:
                await utils.error_handle(ori_self.bot, error, inter)

        return DropdownView()

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
        channel_id: str = commands.Param(
            name="channel",
            description="The channel to move to.",
            autocomplete=move_autocomplete,
        ),
    ):
        try:
            dest_channel = inter.guild.get_channel(int(channel_id))
        except ValueError:
            raise commands.BadArgument("Invalid channel!")

        if not dest_channel:
            raise commands.BadArgument("Invalid channel!")

        await inter.send("Sending...", ephemeral=True)
        await self._move(inter.user, inter, dest_channel)

    @commands.slash_command(
        name="backup-move",
        description=(
            "An alternative way to move if you have an unstable internet connection."
        ),
        guild_ids=[786609181855318047],
        default_permission=False,
    )
    @commands.guild_permissions(786609181855318047, roles=utils.MINI_KG_PERMS)
    @commands.check(move_check)  # type: ignore
    async def backup_move(self, inter: disnake.GuildCommandInteraction):
        can_move = await move_check(inter)
        if not can_move:
            await inter.send(
                "You are not allowed to move at this time.", ephemeral=True
            )
            return

        select_view = await self._create_move_select(inter, inter.user)
        if not select_view:
            await inter.send("There are no channels to move to.", ephemeral=True)
            return

        await inter.send(
            "Please select a channel to move to.", view=select_view, ephemeral=True
        )

    @commands.slash_command(
        name="room-description",
        description="Gets the current room's description during Mini-KGs.",
        guild_ids=[786609181855318047],
        default_permission=False,
    )
    @commands.guild_permissions(786609181855318047, roles=utils.MINI_KG_PERMS)
    async def room_description(self, inter: disnake.GuildCommandInteraction):
        channel = inter.channel
        if isinstance(channel, disnake.Thread):
            channel = channel.parent

        await inter.send(channel.topic)

    @commands.slash_command(
        name="allowed-to-move",
        description="Control if people/everyone should be allowed to move around.",
        guild_ids=[786609181855318047],
        default_permission=False,
    )
    @commands.guild_permissions(786609181855318047, roles=utils.ADMIN_PERMS)
    async def allowed_to_move(
        self,
        inter: disnake.GuildCommandInteraction,
        allowed: bool = commands.Param(
            description="Should the target be able to move around?"
        ),
        user: disnake.Member = commands.Param(
            default=None,
            description=(
                "The user to toggle. If none are provided, all alive players are"
                " affected."
            ),
        ),
    ):
        str_allowed = "T" if allowed else "F"
        if user:
            await inter.bot.redis.hset(
                f"{inter.bot.user.id}{user.id}", "allowed_to_move", str_allowed
            )
        else:
            for member in self.participant_role.members:
                await inter.bot.redis.hset(
                    f"{inter.bot.user.id}{member.id}", "allowed_to_move", str_allowed
                )
        await inter.send("Done!")

    @commands.slash_command(
        name="force-move",
        description="Forcibily move a player to a channel.",
        guild_ids=[786609181855318047],
        default_permission=False,
    )
    @commands.guild_permissions(786609181855318047, roles=utils.ADMIN_PERMS)
    async def force_move(
        self,
        inter: disnake.GuildCommandInteraction,
        user: disnake.Member = commands.Param(description="The user to force move."),
        channel: disnake.TextChannel = commands.Param(
            description="The channel to move the player to."
        ),
    ):
        await inter.response.defer(ephemeral=True)
        await self._move(user, inter, channel)

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

        for member in self.signed_up_role.members:
            # this first line is more or less black magic, but it basically translates characters like 𝓭𝓼𝓰𝓼𝓭𝓰
            # into dsgsdg, which is easier to type
            # source - https://github.com/daveoncode/python-string-utils/blob/78929d/string_utils/manipulation.py#L433
            ascii_name = (
                unicodedata.normalize("NFKD", member.name.lower())
                .encode("ascii", "ignore")
                .decode("utf-8")
            )

            # then this is basically a bunch of basic conversion notes to make the process easier
            # not perfect, but the api can take it from here, i think
            somewhat_valid_name = (
                ascii_name.replace(" ", "-")
                .replace('"', "")
                .replace("'", "")
                .replace(".", "")
            )

            chan = await self.dorm_category.create_text_channel(
                name=f"{somewhat_valid_name}-{member.discriminator}-dorm"
            )
            await self._create_links(chan, self.dorm_link_chan, member)

        await inter.send("Done!")

    @commands.slash_command(
        name="delete-dorms",
        description="Deletes the dorms and their database entries.",
        guild_ids=[786609181855318047],
        default_permission=False,
    )
    @commands.guild_permissions(786609181855318047, roles=utils.ADMIN_PERMS)
    async def delete_dorms(self, inter: disnake.GuildCommandInteraction):
        await inter.response.defer()

        channel_ids = []

        for channel in self.dorm_category.text_channels:
            channel_ids.append(channel.id)
            await channel.delete()

        await models.MovementEntry.filter(
            Q(entry_channel_id__in=channel_ids) | Q(dest_channel_id__in=channel_ids)
        ).delete()

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

            channel_pages: typing.List[typing.Tuple[str, str]] = []

            for channel_id, channel_entries in channel_dict.items():
                chan_entry_strs = [
                    f"<#{e.dest_channel_id}> {f'(<@{e.user_id}>)' if e.user_id else ''}"
                    for e in channel_entries
                ]
                entry_chan = inter.guild.get_channel(channel_id)
                channel_pages.append(
                    (
                        f"Destination channels for #{entry_chan.name}",
                        "\n".join(chan_entry_strs),
                    )
                )

            channel_paginator = paginator.FieldPages(
                inter, entries=channel_pages, per_page=1
            )
            await channel_paginator.paginate()

    @commands.slash_command(
        name="mini-kg-participant-role",
        description="Gives the participant role to everywhone who has signed up.",
        guild_ids=[786609181855318047],
        default_permission=False,
    )
    @commands.guild_permissions(786609181855318047, roles=utils.ADMIN_PERMS)
    async def add_participant_role(self, inter: disnake.GuildCommandInteraction):
        await inter.response.defer()

        for member in self.signed_up_role.members:
            await member.add_roles(self.participant_role)

            if member.get_role(self.spectator_role.id):
                await member.remove_roles(self.spectator_role)

        await inter.send("Done!")

    @commands.slash_command(
        name="remove-mini-kg-roles",
        description="Removes Mini KG roles from people",
        guild_ids=[786609181855318047],
        default_permission=False,
    )
    @commands.guild_permissions(786609181855318047, roles=utils.ADMIN_PERMS)
    async def remove_mini_kg_roles(self, inter: disnake.GuildCommandInteraction):
        await inter.response.defer()

        members = set(self.signed_up_role.members).union(self.participant_role.members)
        roles = (self.signed_up_role, self.participant_role)

        for member in members:
            await member.remove_roles(*roles)

        await inter.send("Done!")

    @commands.slash_command(
        name="sync-mini-kg-rooms",
        description="Syncs Mini-KG room permissions.",
        guild_ids=[786609181855318047],
        default_permission=False,
    )
    @commands.guild_permissions(786609181855318047, roles=utils.ADMIN_PERMS)
    async def sync_mini_kg_rooms(self, inter: disnake.GuildCommandInteraction):
        await inter.response.defer()

        area_category: disnake.CategoryChannel = inter.guild.get_channel(938606024523387000)  # type: ignore
        channels = area_category.text_channels + self.dorm_category.text_channels

        for channel in channels:
            await channel.edit(sync_permissions=True)

        await inter.send("Done!")

    def _create_history_button(self, author_id: int):
        ori_self = self

        class HistoryConfirm(disnake.ui.View):
            def __init__(self):
                super().__init__(timeout=60)
                self.confirmed = False
                self.confirmee: typing.Optional[
                    typing.Union[disnake.User, disnake.Member]
                ] = None

            async def interaction_check(self, inter: disnake.Interaction):
                # funny enough, we want anyone BUT the original author to confirm it
                if inter.author.id == author_id:
                    return False

                if isinstance(inter.author, disnake.Member):
                    # never deny admins
                    if inter.author.guild_permissions.administrator:
                        return True

                    # we dont want mini-kg spectators to confirm
                    if inter.author.get_role(ori_self.spectator_role.id):
                        return False

                return True

            @disnake.ui.button(
                label="Yes, I do.", emoji="✅", style=disnake.ButtonStyle.green
            )
            async def confirm(self, _, inter: disnake.MessageInteraction):
                if inter.author.id == author_id:
                    await inter.send("You can't confirm yourself!", ephemeral=True)
                    return
                if (
                    isinstance(inter.author, disnake.Member)
                    and not inter.author.get_role(ori_self.spectator_role.id)
                    and not inter.author.guild_permissions.administrator
                ):
                    await inter.send(
                        "Mini-KG Spectators can't confirm this!", ephemeral=True
                    )
                    return

                await inter.send("Confirming.", ephemeral=True)
                self.confirmed = True
                self.confirmee = inter.user
                self.stop()

        return HistoryConfirm()

    @commands.slash_command(
        name="view-history",
        description=(
            "DMs the last couple of messages in a channel if given permission by"
            " someone else."
        ),
        guild_ids=[786609181855318047],
        default_permission=False,
    )
    @commands.guild_permissions(786609181855318047, roles=utils.MINI_KG_PERMS)
    async def view_history(self, inter: disnake.GuildCommandInteraction):
        if not (
            inter.channel.category_id
            and inter.channel.category_id in {938606024523387000, 938606098204749914}
        ):
            await inter.send("This command can't be run here!", ephemeral=True)
            return

        await inter.send("Sending request.", ephemeral=True)

        view = self._create_history_button(inter.user.id)
        embed = disnake.Embed(
            title="Message History Request",
            description=(
                f"{inter.user.mention} wishes to view the last few messages from this"
                " channel. Do you wish for them to do so?"
            ),
            color=disnake.Color.orange(),
        )
        embed.set_footer(
            text=(
                "Anyone who is not the requester or a Mini-KG Spectator can accept this"
                " request. To deny this request, simply wait 60 seconds for this"
                " request to time out."
            )
        )

        msg = await inter.channel.send(embed=embed, view=view)
        await view.wait()

        if not view.confirmed:
            embed = disnake.Embed(
                title="Message History Request",
                description=f"{inter.user.mention}'s request timed out.",
                color=disnake.Color.red(),
            )
            await msg.edit(embed=embed, view=None)
        else:
            embed = disnake.Embed(
                title="Message History Request",
                description=(
                    f"{inter.user.mention}'s request was confirmed by"
                    f" {view.confirmee.mention}."
                ),
                color=disnake.Color.green(),
            )
            await msg.edit(embed=embed, view=None)

            LIMIT = 3
            first_message = True
            messages_archived: typing.List[disnake.Message] = []
            count_towards_limit = 0

            async for message in inter.channel.history(limit=16):
                if first_message:
                    # this is the bots confirmation message
                    first_message = False
                    continue

                if "".join(message.content.split()).lower() in {
                    "```end.```",
                    "```end```",
                }:
                    break

                messages_archived.append(message)

                if message.author.id == self.bot.user.id or message.content.startswith(
                    ("/", "(")
                ):
                    continue

                count_towards_limit += 1
                if count_towards_limit >= LIMIT:
                    break

            if not messages_archived:
                await inter.send("There's no messages to view!", ephemeral=True)

            transcript = await chat_exporter.raw_export(
                inter.channel,
                messages=messages_archived,
                guild=inter.guild,
                bot=inter.bot,
            )
            transcript_file = disnake.File(
                io.BytesIO(transcript.encode()),
                filename=f"transcript-{inter.channel.name}.html",
            )

            current_time = disnake.utils.utcnow()
            current_format_time = disnake.utils.format_dt(current_time)

            try:
                msg = await inter.user.send(
                    f"Messages for {inter.channel.name} at {current_format_time} are"
                    " below.\nViewable URL: Getting...",
                    file=transcript_file,
                )

                attachment_url = msg.attachments[0].url
                await msg.edit(
                    content=(
                        f"Messages for {inter.channel.name} at"
                        f" {current_format_time} are below.\nViewable URL:"
                        f" http://htmlpreview.github.io/?{attachment_url}"
                    )
                )
                del transcript_file
            except disnake.Forbidden:
                await inter.send(
                    "Please turn on your DMs for this server! I can't send the message"
                    " history otherwise.",
                    ephemeral=True,
                )
            except disnake.HTTPException:
                await inter.send(
                    "Sending the messages errored out. Please ask someone for the"
                    " messages. Sorry!",
                    ephemeral=True,
                )

    @commands.slash_command(
        name="mini-kg-spectator",
        description=(
            "Adds (or removes) the Mini-KG Spectator role. This role cannot be gotten"
            " by Mini-KG Participants."
        ),
        guild_ids=[786609181855318047],
        default_permission=True,
    )
    async def mini_kg_spectator(self, inter: disnake.GuildCommandInteraction):
        if not isinstance(inter.user, disnake.Member):
            await inter.send(
                "Discord did something weird and I can't add the role. Sorry - please"
                " try again!",
                ephemeral=True,
            )
            return

        if inter.user.get_role(self.participant_role.id):
            await inter.send(
                "You have the Mini-KG Participant role - you can't get this!",
                ephemeral=True,
            )
            return

        if inter.user.get_role(self.spectator_role.id):
            await inter.user.remove_roles(self.spectator_role)
            await inter.send("Removed role!", ephemeral=True)
        else:
            await inter.user.add_roles(self.spectator_role)
            await inter.send("Added role!", ephemeral=True)


def setup(bot: commands.Bot):
    importlib.reload(utils)
    importlib.reload(fuzzys)
    importlib.reload(paginator)
    bot.add_cog(MiniKG(bot))
