import asyncio
import importlib
from datetime import datetime
from typing import Optional

import naff

import common.cards as cards
import common.fuzzy as fuzzy
import common.utils as utils


class CardHandling(utils.Extension):
    def __init__(self, bot):
        self.bot: naff.Client = bot
        self.display_name = "Card Handling"

    @naff.slash_command(
        name="update-card-data",
        description="Updates the internal card data.",
        scopes=[786609181855318047],
        default_member_permissions=naff.Permissions.ADMINISTRATOR,
    )
    async def update_card_data(self, ctx: naff.InteractionContext):
        await ctx.defer()

        importlib.reload(cards)

        extensions = list(self.bot.ext.keys())
        for extension in extensions:
            self.bot.reload_extension(extension)

        await ctx.send("Done!")

    @naff.slash_command(
        name="update-cast",
        description="Updates the cards for the cast.",
        scopes=[786609181855318047],
        default_member_permissions=naff.Permissions.ADMINISTRATOR,
    )
    async def update_cast(self, ctx: naff.InteractionContext):
        await ctx.defer()

        profile_chan: naff.GuildText = ctx.bot.get_channel(786638377801744394)

        def is_valid(m: naff.Message):
            return m.author.id == self.bot.user.id

        reference_date = naff.Timestamp(2021, 9, 2).to_snowflake()
        await profile_chan.purge(
            search_limit=100, predicate=is_valid, after=reference_date
        )

        if cards.hosts:
            await profile_chan.send("```\nKG Hosts\n```")
            embeds = [await host_card.as_embed(self.bot) for host_card in cards.hosts]
            await profile_chan.send(embeds=embeds)

        await profile_chan.send("```\nParticipants\n```")

        embeds = [
            await participant_card.as_embed(self.bot)
            for participant_card in cards.participants
        ]
        chunks = [embeds[x : x + 8] for x in range(0, len(embeds), 8)]

        for chunk in chunks:
            await profile_chan.send(embeds=chunk)
            await asyncio.sleep(1)

        embed = naff.Embed(timestamp=naff.Timestamp.utcnow())
        embed.set_footer(text="Last Updated")

        await profile_chan.send(
            "All participant cards should be in alphabetical order and easily"
            " searchable.\n"
            + "All host cards should be displayed in the order in which they were"
            " revealed.\n"
            + "If any information is wrong, ping or DM Astrea about it and she'll"
            " change it ASAP.",
            embed=embed,
        )

        await ctx.send("Done!")

    @naff.slash_command(
        name="card-search",
        description="Gets you a specific person's card based on the query provided.",
        scopes=[786609181855318047],
    )
    @naff.slash_option(
        "user",
        "The user who RPs the OC on a card.",
        opt_type=naff.OptionTypes.USER,
        required=False,
    )
    @naff.slash_option(
        "oc_name",
        "The name of the OC.",
        opt_type=naff.OptionTypes.STRING,
        required=False,
        autocomplete=True,
    )
    async def card_search(
        self,
        ctx: naff.InteractionContext,
        user: Optional[naff.User] = None,
        oc_name: Optional[str] = None,
    ):
        if user:
            selected_card = next(
                (c for c in cards.participants if c.user_id == user.id), None
            )
            if not selected_card:
                selected_card = next(
                    (c for c in cards.hosts if c.user_id == user.id), None
                )

            if not selected_card:
                raise naff.errors.BadArgument("This user doesn't have a card!")
        elif oc_name:
            selected_card = next(
                c
                for c in tuple(cards.participants + cards.hosts)
                if c.oc_name == oc_name
            )
        else:
            raise naff.errors.BadArgument("No query provided!")

        embed = await selected_card.as_embed(self.bot)
        await ctx.send(embed=embed, ephemeral=True)

    @card_search.autocomplete("oc_name")
    async def wrap(self, ctx, oc_name):
        await fuzzy.fuzzy_autocomplete(ctx, oc_name)


def setup(bot):
    importlib.reload(utils)
    importlib.reload(fuzzy)
    CardHandling(bot)
