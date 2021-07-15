import asyncio
import collections
import importlib

from discord.ext import commands
from discord_slash import ComponentContext
from discord_slash.utils.manage_components import create_actionrow
from discord_slash.utils.manage_components import create_select
from discord_slash.utils.manage_components import create_select_option

import common.cards as cards
import common.utils as utils


def convert_name(oc_name: str):
    """Simple function to convert a name into something that can be used as a value."""
    return oc_name.replace(" ", "").lower()


def get_name_label(oc_name: str):
    """Because sometimes, things don't work out."""

    if len(oc_name) <= 25:
        return oc_name

    name_split = oc_name.split(" ")

    first_last = f"{name_split[0]} {name_split[-1]}"

    if oc_name != first_last and len(first_last) <= 25:
        return first_last

    first = name_split[0]

    if len(first) <= 25:
        return first

    return oc_name[:25]


class Voting(commands.Cog, name="Voting"):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.is_voting = False

    def create_select(self):
        """Creates the select component."""
        options = [
            create_select_option(
                get_name_label(card.oc_name), f"vote:{convert_name(card.oc_name)}"
            )
            for card in cards.participants
        ]
        select = [create_select(options)]
        return [create_actionrow(*select)]

    def vote_check(self, ctx: ComponentContext):
        """Simple check to make sure voting is only done to that one message
        by Alive Players."""
        if ctx.author_id not in self.people_voting:
            return False

        if ctx.origin_message_id != self.voting_msg.id:
            return False

        return True

    @commands.command(aliases=["voting"])
    @utils.proper_permissions()
    async def vote(self, ctx: commands.Context):
        if (
            self.is_voting
        ):  # voting would break if there was more than one vote going on
            raise utils.CustomCheckFailure("There is already a vote going on!")

        actionrow = self.create_select()
        prompt_builder = [
            "It's time to vote! Please use this drop-down menu in order to do so.",
            "Participants have 5 minutes to vote. You may change your vote before the timer runs out.",
        ]

        alive_people_role = ctx.guild.get_role(786610731826544670)  # alive player role
        self.logging_channel = ctx.bot.get_channel(675339100806447125)  # #logs
        self.votes = {}  # will store votes of each person who does
        self.people_voting = frozenset(m.id for m in alive_people_role.members)

        self.voting_msg = await ctx.send(
            "\n".join(prompt_builder), components=actionrow
        )
        self.is_voting = True

        async with ctx.typing():
            try:
                # we abuse timeouts in order to stop this function
                # process_votes runs forever, but wait_for will stop it
                # for running too long
                await asyncio.wait_for(self.process_votes(), 300)
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
        final_msg_builder = [f"{a_tuple[0]}: {a_tuple[1]}" for a_tuple in most_common]
        final_msg_builder.insert(0, "__**VOTES:**__")

        await ctx.send("\n".join(final_msg_builder))

    async def process_votes(self):
        while True:
            ctx: ComponentContext = await self.bot.wait_for(
                "component", check=self.vote_check
            )
            await ctx.defer(hidden=True)  # make sure interact doesnt errror

            card_needed = None

            to_check = ctx.selected_options[0]
            name = to_check.replace("vote:", "")  # get name of option picked

            # should always return a card
            for card in cards.participants:
                if convert_name(card.oc_name) == name:
                    card_needed = card

            self.votes[ctx.author_id] = card_needed.oc_name

            await ctx.send(
                f"Voted for **{card_needed.oc_name}**!", hidden=True
            )  # confirmation message

            # logging message
            embed = utils.error_embed_generate(
                f"<@{ctx.author_id}> voted for **{card_needed.oc_name}**."
            )
            embed.color = ctx.bot.color
            await self.logging_channel.send(embed=embed)


def setup(bot):
    importlib.reload(utils)
    importlib.reload(cards)
    bot.add_cog(Voting(bot))
