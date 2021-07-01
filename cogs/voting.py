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
    return oc_name.replace(" ", "").lower()


class Voting(commands.Cog, name="Voting"):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.is_voting = False

    def create_select(self):
        options = [
            create_select_option(card.oc_name, f"vote:{convert_name(card.oc_name)}")
            for card in cards.participants
        ]

        select = [create_select(options)]
        return [create_actionrow(*select)]

    def vote_check(self, ctx: ComponentContext):
        if ctx.author_id not in self.people_voting:
            return False

        if ctx.origin_message_id != self.voting_msg.id:
            return False

        return True

    @commands.command()
    @utils.proper_permissions()
    async def vote(self, ctx: commands.Context):
        if self.is_voting:
            raise utils.CustomCheckFailure("There is already a vote going on!")

        actionrow = self.create_select()
        prompt_builder = [
            "It's time to vote! Please use this drop-down menu in order to do so.",
            "Participants have 5 minutes to vote. You may change your vote before the timer runs out.",
        ]

        alive_people_role = ctx.guild.get_role(786610731826544670)
        self.votes = {}
        self.people_voting = frozenset(m.id for m in alive_people_role.members)

        self.voting_msg = await ctx.send(
            "\n".join(prompt_builder), components=actionrow
        )
        self.is_voting = True

        try:
            await asyncio.wait_for(self.process_votes(), 300)
        except asyncio.TimeoutError:
            self.is_voting = False

        vote_counter = collections.Counter()
        for value in self.votes.values():
            vote_counter[value] += 1

        most_common = vote_counter.most_common(None)
        final_msg_builder = [f"{a_tuple[0]}: {a_tuple[1]}" for a_tuple in most_common]
        final_msg_builder.insert(0, "__**VOTES:**__")

        await ctx.send("\n".join(final_msg_builder))

    async def process_votes(self):
        while True:
            ctx: ComponentContext = await self.bot.wait_for(
                "component", check=self.vote_check
            )
            await ctx.defer(hidden=True)

            card_needed = None

            to_check = ctx.values[0]
            name = to_check.replace("vote:", "")

            for card in cards.participants:
                if convert_name(card.oc_name) == name:
                    card_needed = card

            self.votes[ctx.author_id] = card_needed.oc_name

            await ctx.send(f"Voted for **{card_needed.oc_name}**!", hidden=True)


def setup(bot):
    importlib.reload(utils)
    importlib.reload(cards)
    bot.add_cog(Voting(bot))
