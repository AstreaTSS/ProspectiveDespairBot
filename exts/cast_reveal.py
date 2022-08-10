#!/usr/bin/env python3.8
import asyncio
import importlib
from copy import copy
from random import shuffle

import naff

import common.cards as cards
import common.utils as utils


class CastReveal(utils.Extension):
    def __init__(self, bot):
        self.bot: naff.Client = bot
        self.name = "Cast Reveal"

    def _generate_components(self, sent: bool = False, disable_all: bool = False):
        return naff.ActionRow(
            naff.Button(
                naff.ButtonStyles.BLURPLE,
                label="Send",
                custom_id="pdcast:send",
                disabled=disable_all or sent,
            ),
            naff.Button(
                naff.ButtonStyles.BLURPLE,
                label="Next",
                custom_id="pdcast:next",
                disabled=disable_all or not sent,
            ),
        )

    @naff.slash_command(
        name="cast-reveal",
        description="A command that automates the cast reveal.",
        scopes=[786609181855318047],
        default_member_permissions=naff.Permissions.ADMINISTRATOR,
    )
    async def cast_reveal(self, ctx: naff.InteractionContext):
        applied = naff.SnowflakeObject(id=786619063023566899)
        alive_player = naff.SnowflakeObject(id=786610731826544670)

        shuffled_participants = copy(cards.participants)
        shuffle(shuffled_participants)

        await ctx.send(
            "Preparing cast reveal. One person will be revealed roughly every minute. "
            + "All entri-- entries--"
        )

        await asyncio.sleep(5)
        await ctx.channel.send(
            embeds=utils.error_embed_generate("Error detected. Retrying...")
        )
        await asyncio.sleep(3)
        await ctx.channel.send("Preparing cast reveal. One person will b")

        await asyncio.sleep(5)
        warning_embed = naff.Embed(
            title="🚨 SYSTEM OVERRIDE DETECTED 🚨", color=naff.MaterialColors.RED
        )
        warning_embed.set_image(
            url="https://cdn.discordapp.com/attachments/968999545621078089/1006651598874886224/WARNING.gif"
        )
        await ctx.channel.send(embeds=warning_embed)

        await asyncio.sleep(3)
        await ctx.channel.send(
            embeds=naff.Embed(title="Shutting down...", color=naff.MaterialColors.RED)
        )

        await asyncio.sleep(0.2)
        beyond_reasoning = ("BEYOND REASONING. " * 30).strip()
        beyond_embed = utils.error_embed_generate(beyond_reasoning)
        beyonds = []
        for _ in range(10):
            m = await ctx.channel.send(embeds=beyond_embed)
            beyonds.append(m)
            await asyncio.sleep(0.1)

        await ctx.channel.delete_messages(beyonds)

        await asyncio.sleep(10)
        await ctx.channel.send(
            embeds=naff.Embed(title="Loading...", color=self.bot.color)
        )

        await asyncio.sleep(3)
        welcome_embed = naff.Embed(color=self.bot.color)
        welcome_embed.set_image(
            url="https://cdn.discordapp.com/attachments/968999545621078089/1006651613261349015/WelcomeMayumi.png"
        )
        await ctx.channel.send(
            embeds=[welcome_embed]
        )  # the embed would otherwise be falsey
        await ctx.channel.send("```\n \n```")

        send_component = self._generate_components(sent=False)
        next_component = self._generate_components(sent=True)
        disabled_component = self._generate_components(disable_all=True)

        def _check_send(event: naff.events.Button):
            return (
                event.context.author.id == self.bot.owner.id
                and event.context.custom_id == "pdcast:send"
            )

        def _check_next(event: naff.events.Button):
            return (
                event.context.author.id == self.bot.owner.id
                and event.context.custom_id == "pdcast:next"
            )

        for index, card in enumerate(shuffled_participants):
            embed = await card.as_embed(self.bot)
            msg = await self.bot.owner.send(
                f"Card {index+1}/{len(shuffled_participants)}",
                embeds=embed,
                components=send_component,
            )

            component_event = await self.bot.wait_for_component(
                msg, send_component, check=_check_send
            )
            await component_event.context.defer(edit_origin=True)

            await ctx.channel.send(
                f"**Welcome {card.title_name}!**\nOC by: {card.mention}",
                embed=embed,
            )
            await ctx.channel.send("```\n \n```")  # looks neater

            if member := ctx.guild.get_member(card.user_id):
                await member.remove_role(int(applied.id))
                # await member.add_role(int(alive_player.id))

            await component_event.context.edit_origin(components=next_component)
            component_event = await self.bot.wait_for_component(
                msg, send_component, check=_check_next
            )
            await component_event.context.edit_origin(components=disabled_component)

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
