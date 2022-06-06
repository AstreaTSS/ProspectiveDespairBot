import importlib
import os
import random

import attrs
import naff

import common.utils as utils


@attrs.define(kw_only=True)
class HostWelcome:
    name: str = attrs.field()
    avatar_url: str = attrs.field()
    color: naff.Color = attrs.field()
    description: str = attrs.field()
    description_no_applications: str = attrs.field()


# sourcery skip: merge-list-append, merge-list-appends-into-extend, merge-list-extend, unwrap-iterable-construction

host_welcomes: list[HostWelcome] = []

host_welcomes.append(
    HostWelcome(
        name="Blake Fleming",
        avatar_url="https://cdn.discordapp.com/attachments/786610535005159425/786715251617038386/image0.png",
        color=naff.Color(0x9B9B9B),
        description=(
            "...welcome to this server, {member}... this server is quite interesting. I"
            " do suggest reading the {rules} of course. You may also be interested in"
            " grabbing a number of roles in {self_roles} or learning about these series"
            " of Killing Games in {kg_info}... although you may simply be looking for"
            " the {applications}. I do highly suggest talking to the server's many"
            " inhabitants in {general} once you are prepared... they are certainly"
            " quite interesting."
        ),
        description_no_applications=(
            "...welcome to this server, {member}... this server is quite interesting. I"
            " do suggest reading the {rules} of course. You may also be interested in"
            " grabbing a number of roles in {self_roles}... or learning about these"
            " series of Killing Games in {kg_info}. I do highly suggest talking to the"
            " server's many inhabitants in {general} once you are prepared... they are"
            " certainly quite interesting."
        ),
    )
)

host_welcomes.append(
    HostWelcome(
        name="Drake Aelius",
        avatar_url="https://cdn.discordapp.com/attachments/675038207955697665/730969036183044106/image0.jpg",
        color=naff.Color(0xB3BE55),
        description=(
            "Ugh, do I have to do this? Fine... welcome to this dumb server, {member}."
            " The {rules} are right there, make sure to read it. You can get some"
            " pathetic roles in {self_roles}, and in case you're a nerd, {kg_info} is"
            " there I guess. If you just want to be done with me, {applications} are"
            " there. Right, you can talk to people in {general}. Can I go now?\n\n[*OOC"
            " Note: This is from an OC/host who, by all measures, was a dick.*]"
        ),
        description_no_applications=(
            "Ugh, do I have to do this? Fine... welcome to this dumb server, {member}."
            " The {rules} are right there, make sure to read it. You can get some"
            " pathetic roles in {self_roles}, and in case you're a nerd, {kg_info} is"
            " there I guess. Right, you can talk to people in {general}. Can I go"
            " now?\n\n[*OOC Note: This is from an OC/host who, by all measures, was a"
            " dick.*]"
        ),
    )
)

host_welcomes.append(
    HostWelcome(
        name="Talia Aelius",
        avatar_url="https://cdn.discordapp.com/attachments/429720487678050308/808461328083058700/taliav2.png",
        color=naff.Color(0x155F60),
        description=(
            "Welcome, {member}~ I hope you have a wonderful time here. The {rules} are"
            " very important, of course! After that, you may want to get some roles at"
            " {self_roles}~ there's also {kg_info}, which has a lot of information"
            " about the Killing Games! But you may already be willing to apply~ in that"
            " case, you'll want to go to {applications}~ Finally, you can check"
            " everyone out in {general}~ I'm sure they're a *delightful* bunch."
        ),
        description_no_applications=(
            "Welcome, {member}~ I hope you have a wonderful time here. The {rules} are"
            " very important, of course! After that, you may want to get some roles at"
            " {self_roles}~ there's also {kg_info}, which has a lot of information"
            " about the Killing Games! Finally, you can check"
            " everyone out in {general}~ I'm sure they're a *delightful* bunch."
        ),
    )
)

host_welcomes.append(
    HostWelcome(
        name="Mayumi Takimura",
        avatar_url="https://media.discordapp.net/attachments/786610508614598696/866495567206678528/image0.jpg",
        color=naff.Color(0xF4AEA2),
        description=(
            "Oh, like welcome {member}! I can't wait to show you around~ there's the"
            " rules at {rules}, you can get some roles at {self_roles}, there's"
            " {kg_info} if you wanna learn about the past or whatever- oops, am I going"
            " too fast? Oh, sorry, but like I don't care. Anyways, there's"
            " {applications} if you wanna apply, and if you wanna talk to people, the"
            " people in {general} are super cool! You can kinda start planning who"
            " you're planning to kill already, hehe..."
        ),
        description_no_applications=(
            "Oh, like welcome {member}! I can't wait to show you around~ there's the"
            " rules at {rules}, you can get some roles at {self_roles}, there's"
            " {kg_info} if you wanna learn about the past or whatever- oops, am I going"
            " too fast? Oh, sorry, but like I don't care. Anyways, if you wanna talk to"
            " people, the people in {general} are super cool! You can kinda start"
            " planning who you're planning to kill already, hehe..."
        ),
    )
)


class Welcome(utils.Extension):
    def __init__(self, bot: naff.Client):
        self.bot = bot

        self.rules = "<#786609893796347944>"
        self.self_roles = "<#786619394209349713>"
        self.kg_info = "<#786642930482937896>"
        self.general = "<#786609182291132437>"
        self.applications = None

        self.webhook = naff.Webhook.from_url(os.environ["WELCOME_WEBHOOK_URL"], bot)
        self.welcome_channel: naff.GuildText = bot.get_channel(824263193303187566)  # type: ignore

    @naff.listen("member_add")
    async def on_member_add(self, event: naff.events.MemberAdd):
        if not self.bot.is_ready or int(event.guild_id) != 786609181855318047:
            return

        host_welcome = random.choice(host_welcomes)
        filled_in_welcome = (
            host_welcome.description
            if self.applications
            else host_welcome.description_no_applications
        )
        filled_in_welcome = filled_in_welcome.format(
            member=event.member.user.mention,
            rules=self.rules,
            self_roles=self.self_roles,
            kg_info=self.kg_info,
            applications=self.applications,
            general=self.general,
        )

        embed = naff.Embed(
            title="Welcome! Here's a greeting from one of our hosts:",
            description=filled_in_welcome,
            color=host_welcome.color,
            timestamp=naff.Timestamp.utcnow(),
        )
        embed.set_footer("Sent at")
        embed.set_author(
            name=event.guild.name,
            icon_url=event.guild.icon.url if event.guild.icon else None,
        )
        embed.set_thumbnail(event.member.display_avatar.url)

        await self.webhook.send(
            content=event.member.user.mention,
            embeds=embed,
            username=host_welcome.name,
            avatar_url=host_welcome.avatar_url,
        )

    @naff.listen("member_remove")
    async def on_member_remove(self, event: naff.events.MemberRemove):
        if not self.bot.is_ready or int(event.guild_id) != 786609181855318047:
            return

        mention = (
            event.member.user.mention
            if isinstance(event.member, naff.Member)
            else event.member.mention
        )

        embed = naff.Embed(
            description=f"Goodbye, {mention} (**{event.member.username}**).",
            color=naff.Color(0xE74C3C),
        )
        await self.welcome_channel.send(embed=embed)


def setup(bot):
    importlib.reload(utils)
    Welcome(bot)
