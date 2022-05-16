#!/usr/bin/env python3.8
import asyncio
import importlib
from copy import deepcopy
from datetime import timedelta
from random import shuffle

import disnake
from disnake.ext import commands

import common.cards as cards


class CastReveal(commands.Cog, name="Cast Reveal"):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.slash_command(
        name="cast-reveal",
        description="A command that automates the cast reveal.",
        guild_ids=[786609181855318047],
        default_permission=False,
    )
    @commands.guild_permissions(786609181855318047, owner=True)
    async def cast_reveal(self, inter: disnake.GuildCommandInteraction):
        await inter.send(
            "Preparing cast reveal. One person will be revealed roughly every minute. "
            + "All entries were randomly shuffled beforehand.\n```\n \n```"
        )

        applied = disnake.Object(786619063023566899)
        alive_player = disnake.Object(786610731826544670)

        shuffled_participants = deepcopy(cards.participants)
        shuffle(shuffled_participants)

        async with inter.channel.typing():
            await asyncio.sleep(20)  # because otherwise it would be done a bit too fast

            for index, card in enumerate(shuffled_participants):
                after_cooldown = disnake.utils.utcnow() + timedelta(seconds=60)

                embed = await card.as_embed(self.bot)
                await inter.channel.send(
                    f"**Welcome {card.title_name}!**\nRPed by: {card.mention}",
                    embed=embed,
                )
                await inter.channel.send("```\n \n```")  # looks neater

                if member := inter.guild.get_member(card.user_id):
                    await member.remove_roles(applied)
                    await member.add_roles(alive_player)

                if index != len(shuffled_participants) - 1:
                    await disnake.utils.sleep_until(after_cooldown)

        await inter.channel.send(
            "**All participants have been revealed.**\nWe apologize if you didn't get"
            " in, "
            + "but there were *a lot* of applications this season. We sadly can't"
            " accept everyone. "
            + "Astrea will be sending a concluding message shortly about backups and"
            " other details."
        )


def setup(bot):
    bot.add_cog(CastReveal(bot))
