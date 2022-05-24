#!/usr/bin/env python3.8
import asyncio
import importlib
from copy import deepcopy
from datetime import timedelta
from random import shuffle

import naff

import common.cards as cards
import common.utils as utils


class CastReveal(utils.Extension):
    def __init__(self, bot):
        self.bot: naff.Client = bot
        self.name = "Cast Reveal"

    @naff.slash_command(
        name="cast-reveal",
        description="A command that automates the cast reveal.",
        scopes=[786609181855318047],
        default_member_permissions=naff.Permissions.ADMINISTRATOR,
    )
    async def cast_reveal(self, ctx: naff.InteractionContext):
        await ctx.send(
            "Preparing cast reveal. One person will be revealed roughly every minute. "
            + "All entries were randomly shuffled beforehand.\n```\n \n```"
        )

        applied = naff.SnowflakeObject(id=786619063023566899)
        alive_player = naff.SnowflakeObject(id=786610731826544670)

        shuffled_participants = deepcopy(cards.participants)
        shuffle(shuffled_participants)

        async with ctx.channel.typing:
            await asyncio.sleep(20)  # because otherwise it would be done a bit too fast

            for index, card in enumerate(shuffled_participants):
                after_cooldown = naff.Timestamp.utcnow() + timedelta(seconds=60)

                embed = await card.as_embed(self.bot)
                await ctx.channel.send(
                    f"**Welcome {card.title_name}!**\nRPed by: {card.mention}",
                    embed=embed,
                )
                await ctx.channel.send("```\n \n```")  # looks neater

                if member := ctx.guild.get_member(card.user_id):
                    await member.remove_roles(applied)
                    await member.add_roles(alive_player)

                if index != len(shuffled_participants) - 1:
                    await utils.sleep_until(after_cooldown)

        await ctx.channel.send(
            "**All participants have been revealed.**\nWe apologize if you didn't get"
            " in, "
            + "but there were *a lot* of applications this season. We sadly can't"
            " accept everyone. "
            + "Astrea will be sending a concluding message shortly about backups and"
            " other details."
        )


def setup(bot):
    importlib.reload(utils)
    CastReveal(bot)
