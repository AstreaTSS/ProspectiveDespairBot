import asyncio
import collections
import importlib

import discord
from discord.ext import commands

import common.cards as cards
import common.utils as utils


def convert_name(oc_name: str):
    """Simple function to convert a name into something that can be used as a value."""
    return oc_name.replace(" ", "").lower()


class Voting(commands.Cog, name="Voting"):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.is_voting = False

    def create_select(self):
        """Creates the select component."""
        ori_self = self

        class Dropdown(discord.ui.Select):
            def __init__(self):
                options = [
                    discord.SelectOption(
                        label=card.oc_name,
                        value=f"vote:{convert_name(card.oc_name)})",
                    )
                    for card in cards.participants
                ]
                super().__init__(min_values=1, max_values=1, options=options)

            async def callback(self, inter: discord.Interaction):
                await inter.response.defer(
                    ephemeral=True
                )  # make sure interact doesnt errror

                card_needed = None

                to_check = self.values[0]
                name = to_check.replace("vote:", "")  # get name of option picked

                # should always return a card
                for card in cards.participants:
                    if convert_name(card.oc_name) == name:
                        card_needed = card

                ori_self.votes[inter.user.id] = card_needed.oc_name

                await inter.followup.send(
                    f"Voted for **{card_needed.oc_name}**!", ephemeral=True
                )  # confirmation message

                # logging message
                embed = utils.error_embed_generate(
                    f"<@{inter.user.id}> voted for **{card_needed.oc_name}**."
                )
                embed.color = ori_self.bot.color
                await ori_self.logging_channel.send(embed=embed)

        class DropdownView(discord.ui.View):
            def __init__(self):
                super().__init__()
                self.add_item(Dropdown())

            async def interaction_check(self, interaction: discord.Interaction) -> bool:
                return interaction.user.id in ori_self.people_voting

        return DropdownView()

    @commands.command(aliases=["voting"])
    @utils.proper_permissions()
    async def vote(self, ctx: commands.Context):
        if (
            self.is_voting
        ):  # voting would break if there was more than one vote going on
            raise utils.CustomCheckFailure("There is already a vote going on!")

        voting_view = self.create_select()
        prompt_builder = [
            "It's time to vote! Please use this drop-down menu in order to do so.",
            "Participants have 5 minutes to vote. You may change your vote before the timer runs out.",
        ]

        alive_people_role = ctx.guild.get_role(673640411494875182)  # alive player role
        self.logging_channel = ctx.bot.get_channel(675339100806447125)  # #logs
        self.votes = {}  # will store votes of each person who does
        self.people_voting = frozenset(m.id for m in alive_people_role.members)

        self.voting_msg = await ctx.send("\n".join(prompt_builder), view=voting_view)
        self.is_voting = True

        async with ctx.typing():
            try:
                # we abuse timeouts in order to stop this function
                # process_votes runs forever, but wait_for will stop it
                # for running too long
                await asyncio.wait_for(voting_view.stop(), 300)
            except asyncio.TimeoutError:
                self.is_voting = False
                await voting_view.stop()

        # transfer the format of [discord_user_id] = 'oc name'
        # to ['oc name'] = number_of_votes
        vote_counter = collections.Counter()
        for value in self.votes.values():
            vote_counter[value] += 1

        most_common = vote_counter.most_common(
            None
        )  # [('oc name', num of votes)] from most to least votes
        final_msg_builder = [f"{a_tuple[0]}: {a_tuple[1]}" for a_tuple in most_common]
        final_msg_builder.insert(0, "__**VOTES:**__")

        await ctx.send("\n".join(final_msg_builder))


def setup(bot):
    importlib.reload(utils)
    importlib.reload(cards)
    bot.add_cog(Voting(bot))
