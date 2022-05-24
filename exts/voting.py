import asyncio
import collections
import importlib
import typing

import naff

import common.cards as cards
import common.utils as utils


def convert_name(name: typing.Any):
    """Simple function to convert a name into something that can be used as a value."""
    return str(name).replace(" ", "").lower()


class Voting(utils.Extension):
    def __init__(self, bot):
        self.bot: naff.Client = bot
        self.name = "Voting"
        self.is_voting = False

    async def _handle_input(
        self,
        ctx: naff.ComponentContext,
        full_list: list,
        attr_name: str,
        display_attr_name: typing.Optional[str] = None,
    ):
        await ctx.defer(ephemeral=True)

        item_needed = None

        to_check: str = ctx.values[0]
        name = to_check.removeprefix("vote:")  # get name of option picked

        # should always return something
        for item in full_list:
            if convert_name(getattr(item, attr_name)) == name:
                item_needed = item

        assert item_needed != None

        display_name = getattr(item_needed, str(display_attr_name))
        internal_name = convert_name(getattr(item_needed, attr_name))

        self.votes[ctx.author.id] = internal_name

        await ctx.send(
            f"Voted for **{display_name}**!", ephemeral=True
        )  # confirmation message

        # logging message
        embed = utils.error_embed_generate(
            f"<@{ctx.author.id}> voted for **{display_name}**."
        )
        embed.color = self.bot.color
        await self.logging_channel.send(embed=embed)

    async def handle_voting(
        self,
        select: naff.Select,
        full_list: list,
        attr_name: str,
        display_attr_name: typing.Optional[str] = None,
    ):
        if not display_attr_name:
            display_attr_name = attr_name

        def check(sel: naff.events.Component):
            return sel.context.author.id in self.people_voting

        while True:
            sel_event = await self.bot.wait_for_component(
                components=select, check=check
            )
            # we don't want to make this function lag behind
            asyncio.create_task(
                self._handle_input(
                    sel_event.context, full_list, attr_name, display_attr_name
                )
            )

    @naff.slash_command(
        name="vote",
        description="Starts the automatic voting system for trials.",
        scopes=[786609181855318047],
        default_member_permissions=naff.Permissions.ADMINISTRATOR,
    )
    async def vote(self, ctx: naff.InteractionContext):
        if (
            self.is_voting
        ):  # voting would break if there was more than one vote going on
            raise utils.CustomCheckFailure("There is already a vote going on!")

        await ctx.defer()

        options = [
            naff.SelectOption(
                label=card.oc_name,
                value=f"vote:{convert_name(card.oc_name)}",
            )
            for card in cards.participants
        ]
        voting_select = naff.Select(options=options)
        prompt_builder = [
            "It's time to vote! Please use this drop-down menu in order to do so.",
            "Participants have 5 minutes to vote. You may change your vote before the"
            " timer runs out.",
        ]

        alive_people_role = ctx.guild.get_role(786610731826544670)  # alive player role
        self.logging_channel = self.bot.get_channel(786622913587576832)  # #logs
        self.votes = {}  # will store votes of each person who does
        self.people_voting = frozenset(m.id for m in alive_people_role.members)

        self.voting_msg = await ctx.send(
            content="\n".join(prompt_builder),
            components=voting_select,
        )
        self.is_voting = True

        async with ctx.channel.typing:
            try:
                await asyncio.wait_for(
                    self.handle_voting(voting_select, cards.participants, "oc_name"),
                    300,
                )
            except asyncio.TimeoutError:
                self.is_voting = False

        # transfer the format of [discord_user_id] = 'oc name'
        # to ['oc name'] = number_of_votes
        vote_counter = collections.Counter()
        for value in self.votes.values():
            vote_counter[value] += 1

        most_common = vote_counter.most_common(
            None
        )  # [('oc name', num of votes)] from most to least votes
        final_msg_builder = [
            f"**{a_tuple[0]}**: {a_tuple[1]}" for a_tuple in most_common
        ]
        final_msg_builder.insert(0, "__**VOTES:**__\n")

        await ctx.channel.send("\n".join(final_msg_builder))

        voting_select.disabled = True
        await self.voting_msg.edit(
            content="\n".join(prompt_builder), components=voting_select
        )


def setup(bot):
    importlib.reload(utils)
    Voting(bot)
