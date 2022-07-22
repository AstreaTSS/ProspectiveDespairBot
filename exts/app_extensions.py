import importlib
from enum import Enum

import naff

import common.utils as utils


class ExtAppStatus(Enum):
    PENDING = naff.RoleColors.ORANGE
    ACCEPTED = naff.RoleColors.GREEN
    DENIED = naff.RoleColors.RED


class ApplicationExtensions(utils.Extension):
    def __init__(self, bot: naff.Client):
        self.bot: naff.Client = bot
        self.name = "Application Extensions"

        self.bot.register_function(self._get_required_info())

    async def _get_required_info(self):
        self.app_channel: naff.GuildText = await self.bot.fetch_channel(866667283094962196)  # type: ignore
        self.admin_channel: naff.GuildText = await self.bot.fetch_channel(786610508614598696)  # type: ignore
        self.asked_for_ext: naff.Role = await self.admin_channel.guild.fetch_role(819913170196889602)  # type: ignore
        self.has_ext: naff.Role = await self.admin_channel.guild.fetch_role(986462545516843068)  # type: ignore

    @naff.prefixed_command()
    @utils.proper_permissions()
    async def send_extension_modal(self, ctx: naff.InteractionContext):
        button = naff.Button(
            style=naff.ButtonStyles.PRIMARY,
            label="Apply",
            emoji="📩",
            custom_id="pd-button:extension_ask",
        )

        embed = naff.Embed(
            title="Apply for an Extension",
            description=(
                "Hey! If you're reading this, extensions are now available! They'll"
                " give you three extra days from the deadline to finish up your"
                " application.\n\n**Extensions are not given out to everyone. They will"
                " only be given to people who need it due to unfortunate"
                " circumstances.**\n\nValid reasons for an extension include (but are"
                " not limited to):\n- A major life event happened, and you need some"
                " time to recover.\n- You've had a very low motivation period recently,"
                " but want to complete your application.\n- You got busy at the last"
                " minute right before the deadline, and you just need a bit more time"
                " to finish it.\n\nAs much as we hate saying it, *procrastination is"
                " not a valid excuse.* Extensions delay our rating process and make it"
                " more complex, so we'd prefer if we do not have too many of"
                " them.\n\nTo apply for an extension, click the button below. A prompt"
                " will open up asking you why you want an extension.\nMake sure your"
                " DMs are turned on for this server if they aren't already. This is the"
                " only way we can contact you about your decision.\n*You may only apply"
                " once. DM an admin if you disagree with your decision.*"
            ),
            color=self.bot.color,
        )
        embed.set_author(
            name=ctx.guild.name,
            icon_url=ctx.guild.icon.url if ctx.guild.icon else None,
        )

        await ctx.send(embeds=embed, components=button)
        await ctx.message.delete()

    @naff.component_callback("pd-button:extension_ask")  # type: ignore
    async def on_extension_ask_button(self, ctx: naff.ComponentContext):
        if ctx.author.has_role(self.asked_for_ext):
            await ctx.send("You already asked for an extension!", ephemeral=True)
        else:
            modal = naff.Modal(
                title="Application for Extension",
                components=[
                    naff.ParagraphText(
                        label="Why do you need an extension?",
                        custom_id="ext_reasoning",
                        placeholder=(
                            "Whatever you put will be admin to the mods for approval."
                        ),
                        max_length=3900,
                    )
                ],
                custom_id="pd-modal:extension_ask",
            )
            await ctx.send_modal(modal)

    def generate_extension_embed(
        self,
        ctx: naff.Context,
        member: naff.Member,
        description: str,
        status: ExtAppStatus = ExtAppStatus.PENDING,
    ):
        embed = naff.Embed(
            title=f"Extension Application by {member.display_name}",
            description=description,
            color=status.value,
            fields=[
                naff.EmbedField(name="Applicant", value=member.mention, inline=True),
                naff.EmbedField(name="Status", value=status.name.title(), inline=True),
            ],
        )
        embed.set_author(
            name=ctx.guild.name,
            icon_url=ctx.guild.icon.url if ctx.guild.icon else None,
        )
        embed.set_thumbnail(member.display_avatar.url)
        embed.set_footer(
            "All denials require a reason. This will be asked of you when you deny it."
            " Only one admin needs to decide on this."
        )
        return embed

    def generate_actionrow(self, member: naff.Member, *, disabled: bool = False):
        return naff.ActionRow(
            naff.Button(
                style=naff.ButtonStyles.GREEN,
                label="Accept",
                emoji="✅",
                custom_id=f"pd-button:approval_extension|accept-{member.id}",
                disabled=disabled,
            ),
            naff.Button(
                style=naff.ButtonStyles.RED,
                label="Deny",
                emoji="✖️",
                custom_id=f"pd-button:approval_extension|deny-{member.id}",
                disabled=disabled,
            ),
        )

    @naff.listen("modal_response")
    async def on_extension_ask_modal(self, event: naff.events.ModalResponse):
        ctx = event.context

        if ctx.custom_id == "pd-modal:extension_ask":
            await ctx.author.add_role(self.asked_for_ext)
            embed = self.generate_extension_embed(
                ctx, ctx.author, ctx.responses["ext_reasoning"]
            )
            actionrow = self.generate_actionrow(ctx.author)
            await self.admin_channel.send(embed=embed, components=actionrow)
            await ctx.send("Sent!", ephemeral=True)

    @naff.listen("component")
    async def on_extension_accept_deny(self, event: naff.events.Component):
        ctx = event.context

        if ctx.custom_id.startswith("pd-button:approval_extension|accept"):
            member_id = int(
                ctx.custom_id.removeprefix("pd-button:approval_extension|accept-")
            )
            member = await ctx.guild.fetch_member(member_id)

            if not member:
                await ctx.send(
                    "This member doesn't seem to be in the server - did they leave?",
                    ephemeral=True,
                )
                return

            await member.add_role(self.has_ext)

            desc: str = ctx.message.embeds[0].description
            embed = self.generate_extension_embed(
                ctx,
                member,
                desc,
                status=ExtAppStatus.ACCEPTED,
            )
            actionrow = self.generate_actionrow(member, disabled=True)
            embed.add_field(name="Accepted by", value=ctx.author.mention, inline=True)
            await ctx.message.edit(
                content=f"Approved by {ctx.author.mention}.",
                embeds=embed,
                components=actionrow,
            )
            await ctx.send("Approved!", ephemeral=True)
        elif ctx.custom_id.startswith("pd-button:approval_extension|deny-"):
            member_id = int(
                ctx.custom_id.removeprefix("pd-button:approval_extension|deny-")
            )
            member = await ctx.guild.fetch_member(member_id)

            if not member:
                await ctx.send(
                    "This member doesn't seem to be in the server - did they leave?",
                    ephemeral=True,
                )
                return

            modal = naff.Modal(
                title=f"Rejecting {member.display_name}",
                components=[
                    naff.ParagraphText(
                        label="Why did you reject them?",
                        custom_id="reject_reason",
                        max_length=1000,
                    )
                ],
                custom_id=f"pd-modal:ext_reject|{ctx.message.id}-{member_id}",
            )

            await ctx.send_modal(modal)

    @naff.listen("modal_response")
    async def on_extension_deny_modal(self, event: naff.events.ModalResponse):
        ctx = event.context

        if ctx.custom_id.startswith("pd-modal:ext_reject|"):
            no_prefix = ctx.custom_id.removeprefix("pd-modal:ext_reject|")

            message_id, member_id = no_prefix.split("-")

            message = await self.admin_channel.fetch_message(int(message_id))
            if not message:
                await ctx.send(
                    "The message for this application was deleted.",
                    ephemeral=True,
                )
                return

            member = await ctx.guild.fetch_member(int(member_id))

            if not member:
                await ctx.send(
                    "This member doesn't seem to be in the server - did they leave?",
                    ephemeral=True,
                )
                return

            desc: str = message.embeds[0].description
            embed = self.generate_extension_embed(
                ctx,
                member,
                desc,
                status=ExtAppStatus.DENIED,
            )
            embed.add_field(name="Denied by", value=ctx.author.mention, inline=False)
            embed.add_field(name="Reason", value=ctx.responses["reject_reason"])
            actionrow = self.generate_actionrow(member, disabled=True)
            await message.edit(
                content=f"Denied by {ctx.author.mention}.",
                embeds=embed,
                components=actionrow,
            )
            await ctx.send("Denied.", ephemeral=True)


def setup(bot):
    importlib.reload(utils)
    ApplicationExtensions(bot)
