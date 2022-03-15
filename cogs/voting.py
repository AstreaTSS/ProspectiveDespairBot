import asyncio
import collections
import importlib
import typing

import disnake
from disnake.ext import commands

import common.cards as cards
import common.models as models
import common.utils as utils


def convert_name(name: str):
    """Simple function to convert a name into something that can be used as a value."""
    return str(name).replace(" ", "").lower()


class Voting(commands.Cog, name="Voting"):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.is_voting = False

    def create_select(
        self,
        options: typing.List[disnake.SelectOption],
        full_list: typing.List,
        attr_name: str,
        disabled: bool = False,
    ):
        """Creates the select component."""
        ori_self = self

        class Dropdown(disnake.ui.Select):
            def __init__(self):
                super().__init__(
                    min_values=1, max_values=1, options=options, disabled=disabled
                )

            async def callback(self, inter: disnake.Interaction):
                await inter.response.defer(
                    ephemeral=True
                )  # make sure interact doesnt errror

                item_needed = None

                to_check = self.values[0]
                name = to_check.replace("vote:", "")  # get name of option picked

                # should always return something
                for item in full_list:
                    if convert_name(getattr(item, attr_name)) == name:
                        item_needed = item

                assert item_needed != None
                display_name = getattr(item_needed, attr_name)

                ori_self.votes[inter.user.id] = display_name

                await inter.followup.send(
                    f"Voted for **{display_name}**!", ephemeral=True
                )  # confirmation message

                # logging message
                embed = utils.error_embed_generate(
                    f"<@{inter.user.id}> voted for **{display_name}**."
                )
                embed.color = ori_self.bot.color
                await ori_self.logging_channel.send(embed=embed)

        class DropdownView(disnake.ui.View):
            def __init__(self):
                super().__init__()
                self.add_item(Dropdown())

            async def interaction_check(self, interaction: disnake.Interaction) -> bool:
                return interaction.user.id in ori_self.people_voting

            async def on_error(
                self, error: Exception, _, inter: disnake.MessageInteraction
            ) -> None:
                await utils.error_handle(ori_self.bot, error, inter)

        return DropdownView()

    @commands.slash_command(
        name="vote",
        description="Starts the automatic voting system for trials.",
        guild_ids=[786609181855318047],
        default_permission=False,
    )
    @commands.guild_permissions(786609181855318047, roles=utils.ADMIN_PERMS)
    async def vote(self, inter: disnake.GuildCommandInteraction):
        if (
            self.is_voting
        ):  # voting would break if there was more than one vote going on
            raise utils.CustomCheckFailure("There is already a vote going on!")

        await inter.response.defer()

        options = [
            disnake.SelectOption(
                label=card.oc_name,
                value=f"vote:{convert_name(card.oc_name)}",
            )
            for card in cards.participants
        ]
        voting_view = self.create_select(options, cards.participants, "oc_name")
        prompt_builder = [
            "It's time to vote! Please use this drop-down menu in order to do so.",
            "Participants have 5 minutes to vote. You may change your vote before the"
            " timer runs out.",
        ]

        alive_people_role = inter.guild.get_role(
            786610731826544670
        )  # alive player role
        self.logging_channel = self.bot.get_channel(786622913587576832)  # #logs
        self.votes = {}  # will store votes of each person who does
        self.people_voting = frozenset(m.id for m in alive_people_role.members)

        self.voting_msg = await inter.edit_original_message(
            content="\n".join(prompt_builder), view=voting_view
        )
        self.is_voting = True

        async with inter.channel.typing():
            try:
                # we abuse timeouts in order to stop this function
                # process_votes runs forever, but wait_for will stop it
                # for running too long
                await asyncio.wait_for(voting_view.wait(), 300)
            except asyncio.TimeoutError:
                self.is_voting = False
                voting_view.stop()

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

        await inter.channel.send("\n".join(final_msg_builder))

        voting_view = self.create_select(
            options, cards.participants, "oc_name", disabled=True
        )
        await self.voting_msg.edit(content="\n".join(prompt_builder), view=voting_view)
        voting_view.stop()

    @commands.slash_command(
        name="vote-mini-kg",
        description="Starts the automatic voting system for Mini-KG trials.",
        guild_ids=[786609181855318047],
        default_permission=False,
    )
    @commands.guild_permissions(786609181855318047, roles=utils.ADMIN_PERMS)
    async def vote_mini_kg(self, inter: disnake.GuildCommandInteraction):
        if (
            self.is_voting
        ):  # voting would break if there was more than one vote going on
            raise utils.CustomCheckFailure("There is already a vote going on!")

        await inter.response.defer()

        participant_role = inter.guild.get_role(
            939993631140495360
        )  # mini-kg participant role
        participant_role_members = participant_role.members
        self.people_voting = frozenset(m.id for m in participant_role_members)

        options = [
            disnake.SelectOption(
                label=f"{member.display_name} ({member})",
                value=f"vote:{member.id}",
            )
            for member in participant_role_members
        ]
        voting_view = self.create_select(options, participant_role_members, "id")
        prompt_builder = [
            "It's time to vote! Please use this drop-down menu in order to do so.",
            "Participants have 5 minutes to vote. You may change your vote before the"
            " timer runs out.",
            "(Vote for the *user whose OC is the blackened* - do *not* vote by their OC's"
            " name.)",
        ]

        self.logging_channel = self.bot.get_channel(786622913587576832)  # #logs
        self.votes = {}  # will store votes of each person who does

        self.voting_msg = await inter.edit_original_message(
            content="\n".join(prompt_builder), view=voting_view
        )
        self.is_voting = True

        async with inter.channel.typing():
            try:
                # we abuse timeouts in order to stop this function
                # process_votes runs forever, but wait_for will stop it
                # for running too long
                await asyncio.wait_for(voting_view.wait(), 300)
            except asyncio.TimeoutError:
                self.is_voting = False
                voting_view.stop()

        vote_weight_dict = {}
        async for user_entry in models.MiniKGPoints.filter(
            user_id__in=list(self.people_voting)
        ):
            vote_weight_dict[user_entry.user_id] = (
                user_entry.points if user_entry.points >= 1 else 0.5
            )

        # transfer the format of [discord_user_id] = 'voted name'
        # to ['voted name'] = number_of_votes
        vote_counter = collections.Counter()
        for user_id, vote in self.votes.items():
            vote_counter[vote] += vote_weight_dict[user_id]

        most_common = vote_counter.most_common(
            None
        )  # [('voted name', num of votes)] from most to least votes
        final_msg_builder = [
            f"**{a_tuple[0]}**: {a_tuple[1]}" for a_tuple in most_common
        ]
        final_msg_builder.insert(0, "__**WEIGHTED VOTES:**__\n")

        await inter.channel.send("\n".join(final_msg_builder))

        voting_view = self.create_select(
            options, participant_role_members, "id", disabled=True
        )
        await self.voting_msg.edit(content="\n".join(prompt_builder), view=voting_view)
        voting_view.stop()


def setup(bot):
    importlib.reload(utils)
    bot.add_cog(Voting(bot))
