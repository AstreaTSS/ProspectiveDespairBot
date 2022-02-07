import importlib

import disnake
from disnake.ext import commands

import common.fuzzys as fuzzys
import common.models as models
import common.utils as utils


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

    deny = disnake.PermissionOverwrite(
        view_channel=False, send_messages=False, send_messages_in_threads=False
    )
    allow = disnake.PermissionOverwrite(
        view_channel=True, send_messages=True, send_messages_in_threads=True
    )

    async def _move(
        self, inter: disnake.GuildCommandInteraction, dest_channel: disnake.TextChannel
    ):
        entry_channel = inter.channel
        if isinstance(entry_channel, disnake.Thread):
            entry_channel = entry_channel.parent

        await entry_channel.set_permissions(inter.user, overwrite=self.deny)
        await dest_channel.set_permissions(inter.user, overwrite=self.allow)

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
        await self._move(inter, dest_channel)

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

        participants = inter.guild.get_role(939993631140495360)
        for member in participants.members:
            await self._move(inter, channel)

        await inter.send("Done!", ephemeral=True)


def setup(bot: commands.Bot):
    importlib.reload(utils)
    importlib.reload(fuzzys)
    bot.add_cog(Movement(bot))
