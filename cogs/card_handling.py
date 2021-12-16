import asyncio
import importlib
from datetime import datetime
from typing import Optional
from typing import Union

import disnake
from disnake.ext import commands

import common.cards as cards
import common.fuzzys as fuzzys
import common.utils as utils


class CardHandling(commands.Cog, name="Card Handling"):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.command()
    @commands.is_owner()
    async def update_card_data(self, ctx: commands.Context):
        importlib.reload(cards)

        extensions = [i for i in self.bot.extensions.keys()]
        for extension in extensions:
            self.bot.reload_extension(extension)

        await ctx.reply("Done!")

    @commands.command()
    @utils.proper_permissions()
    async def update_cast(self, ctx: commands.Context):

        async with ctx.typing():
            profile_chan: disnake.TextChannel = self.bot.get_channel(786638377801744394)

            def is_valid(m: disnake.Message):
                return m.author.id == self.bot.user.id

            reference_date = datetime(2021, 9, 2)
            await profile_chan.purge(limit=100, check=is_valid, after=reference_date)

            if cards.hosts:
                await profile_chan.send("```\nKG Hosts\n```")
                embeds = [
                    await host_card.as_embed(ctx.bot) for host_card in cards.hosts
                ]
                await profile_chan.send(embeds=embeds)

            await profile_chan.send("```\nParticipants\n```")

            embeds = [
                await participant_card.as_embed(ctx.bot)
                for participant_card in cards.participants
            ]
            chunks = [embeds[x : x + 8] for x in range(0, len(embeds), 8)]

            for chunk in chunks:
                await profile_chan.send(embeds=chunk)
                await asyncio.sleep(1)

            embed = disnake.Embed(timestamp=disnake.utils.utcnow())
            embed.set_footer(text="Last Updated")

            await profile_chan.send(
                "All participant cards should be in alphabetical order and easily searchable.\n"
                + "All host cards should be displayed in the order in which they were revealed.\n"
                + "If any information is wrong, ping or DM Astrea about it and she'll change it ASAP.",
                embed=embed,
            )

        await ctx.reply("Done!")

    @commands.slash_command(
        name="query",
        description="Gets you a specific person's card based on the query provided.",
        guild_ids=[786609181855318047],
        default_permission=False,
    )
    @commands.guild_permissions(786609181855318047, owner=True)
    async def query(
        self,
        inter: disnake.GuildCommandInteraction,
        user: Optional[disnake.User] = commands.Param(
            default=None, description="The user who RPs the OC on a card."
        ),
        oc_name: Optional[str] = commands.Param(
            default=None, autocomplete=fuzzys.get_card_name
        ),
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
                raise commands.BadArgument("This user doesn't have a card!")
        elif oc_name:
            selected_card = next(
                c
                for c in tuple(cards.participants + cards.hosts)
                if c.oc_name == oc_name
            )
        else:
            raise commands.BadArgument("No query provided!")

        embed = await selected_card.as_embed(self.bot)
        await inter.send(embed=embed, ephemeral=True)


def setup(bot):
    importlib.reload(utils)
    importlib.reload(fuzzys)
    bot.add_cog(CardHandling(bot))
