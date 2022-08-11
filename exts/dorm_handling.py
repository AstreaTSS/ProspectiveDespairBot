import asyncio
import importlib

import naff

import common.cards as cards
import common.utils as utils


class DormHandling(utils.Extension):
    def __init__(self, bot):
        self.bot: naff.Client = bot
        self.name = "Dorm Handling"
        self.room_description: str = None  # type: ignore

        asyncio.create_task(self.async_init())

    async def async_init(self):
        await self.bot.wait_until_ready()

        base_room: naff.GuildText = self.bot.get_channel(921453015595118612)  # type: ignore
        message: naff.Message = await base_room.fetch_message(1007124865469390939)  # type: ignore

        self.room_description = message.content
        self.dorm_category: naff.GuildCategory = base_room.category  # type: ignore
        self.dorm_channel_format = base_room.name.split("base-room")  # type: ignore

    @naff.slash_command(
        name="create-dorms",
        description="A command that creates all of the dorms needed.",
        scopes=[786609181855318047],
        default_member_permissions=naff.Permissions.ADMINISTRATOR,
    )
    async def create_dorms(self, ctx: naff.InteractionContext):
        await ctx.defer()

        for participant in cards.participants:
            name_friendly = participant.oc_name.lower().replace(" ", "-")
            channel_name = f"{self.dorm_channel_format[0]}{name_friendly}{self.dorm_channel_format[1]}"

            new_chan = await self.dorm_category.create_text_channel(
                channel_name, reason=f"Creating dorm for {participant.oc_name}"
            )
            room_description = self.room_description.format(
                name=participant.oc_name, talent=participant.oc_talent
            )
            desc_msg = await new_chan.send(
                room_description, allowed_mentions=naff.AllowedMentions.none()
            )
            await desc_msg.pin()

        await ctx.send("Done!")

    async def _update_dorm_data(self):
        base_room: naff.GuildText = self.bot.get_channel(921453015595118612)  # type: ignore
        message: naff.Message = await base_room.fetch_message(1007124865469390939)  # type: ignore

        self.room_description = message.content
        self.dorm_category: naff.GuildCategory = base_room.category  # type: ignore
        self.dorm_channel_format = base_room.name.split("base-room")  # type: ignore

    @naff.slash_command(
        name="edit-dorms",
        description="Edit the dorms with the new description.",
        scopes=[786609181855318047],
        default_member_permissions=naff.Permissions.ADMINISTRATOR,
    )
    async def edit_dorms(self, ctx: naff.InteractionContext):
        await ctx.defer()

        await self._update_dorm_data()
        dorm_mapping = {
            c.name: c for c in self.dorm_category.text_channels  # type: ignore
        }

        for participant in cards.participants:
            name_friendly = participant.oc_name.lower().replace(" ", "-")
            channel_name = f"{self.dorm_channel_format[0]}{name_friendly}{self.dorm_channel_format[1]}"

            if dorm := dorm_mapping.get(channel_name):
                pins = await dorm.fetch_pinned_messages()
                desc_msg = pins[-1]  # we can only hope it is, anyways
                room_description = self.room_description.format(
                    name=participant.oc_name, talent=participant.oc_talent
                )
                await desc_msg.edit(content=room_description)

        await ctx.send("Done!")

    @naff.slash_command(
        name="add-dorms-for-missing",
        description="Add dorms for missing people.",
        scopes=[786609181855318047],
        default_member_permissions=naff.Permissions.ADMINISTRATOR,
    )
    async def add_dorms_for_missing(self, ctx: naff.InteractionContext):
        await ctx.defer()

        await self._update_dorm_data()
        dorm_mapping = {
            c.name: c for c in self.dorm_category.text_channels  # type: ignore
        }

        for participant in cards.participants:
            name_friendly = participant.oc_name.lower().replace(" ", "-")
            channel_name = f"{self.dorm_channel_format[0]}{name_friendly}{self.dorm_channel_format[1]}"

            if not dorm_mapping.get(channel_name):
                new_chan = await self.dorm_category.create_text_channel(
                    channel_name, reason=f"Creating dorm for {participant.oc_name}"
                )
                room_description = self.room_description.format(
                    name=participant.oc_name, talent=participant.oc_talent
                )
                desc_msg = await new_chan.send(
                    room_description, allowed_mentions=naff.AllowedMentions.none()
                )
                await desc_msg.pin()

        await ctx.send("Done!")


def setup(bot):
    importlib.reload(utils)
    DormHandling(bot)
