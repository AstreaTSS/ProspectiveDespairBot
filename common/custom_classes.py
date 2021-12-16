#!/usr/bin/env python3.8
import asyncio
import typing

import attr
import disnake
from disnake.ext import commands

import common.utils as utils


@attr.s(slots=True)
class WizardQuestion:
    question: str = attr.ib()
    converter: typing.Callable = attr.ib()
    action: typing.Callable = attr.ib()


@attr.s
class WizardManager:
    """A class that allows you to make a wizard of sorts, allowing a more intuitive way of getting multiple inputs from a user."""

    embed_title: str = attr.ib()
    final_text: str = attr.ib()
    color: disnake.Color = attr.ib(default=disnake.Color(0x2EBAE1))
    timeout: float = attr.ib(default=120)
    pass_self: bool = attr.ib(default=False)

    questions: typing.List[WizardQuestion] = attr.ib(factory=list, init=False)
    ori_mes: typing.Optional[disnake.Message] = attr.ib(default=None, init=False)

    def add_question(
        self, question: str, converter: typing.Callable, action: typing.Callable
    ):
        self.questions.append(WizardQuestion(question, converter, action))

    async def run(self, ctx: commands.Context):
        def check(m: disnake.Message):
            return m.author == ctx.author and m.channel == ctx.channel

        wizard_embed = disnake.Embed(title=self.embed_title, colour=self.color)
        wizard_embed.set_author(
            name=f"{ctx.bot.user.name}",
            icon_url=utils.get_icon_url(ctx.guild.me.display_avatar),
        )
        wizard_embed.set_footer(
            text="If you wish to stop this setup at any time, just type in 'exit'."
        )

        for question in self.questions:
            wizard_embed.description = question.question

            if not self.ori_mes:
                self.ori_mes = await ctx.reply(embed=wizard_embed)
            else:
                await self.ori_mes.edit(embed=wizard_embed)

            try:
                reply: disnake.Message = await ctx.bot.wait_for(
                    "message", check=check, timeout=self.timeout
                )
            except asyncio.TimeoutError:
                wizard_embed.description = "Failed to reply. Exiting..."
                wizard_embed.set_footer(text=disnake.Embed.Empty)
                await self.ori_mes.edit(embed=wizard_embed)
                return
            else:
                if reply.content.lower() == "exit":
                    wizard_embed.description = "Exiting..."
                    wizard_embed.set_footer(text=disnake.Embed.Empty)
                    await self.ori_mes.edit(embed=wizard_embed)
                    return

            try:
                converted = await disnake.utils.maybe_coroutine(
                    question.converter, ctx, reply.content
                )
            except Exception as e:  # base exceptions really shouldn't be caught
                wizard_embed.description = (
                    f"Invalid input. Exiting...\n\nError: {str(e)}"
                )
                wizard_embed.set_footer(text=disnake.Embed.Empty)
                await self.ori_mes.edit(embed=wizard_embed)
                return

            if not self.pass_self:
                await disnake.utils.maybe_coroutine(question.action, ctx, converted)
            else:
                await disnake.utils.maybe_coroutine(
                    question.action, ctx, converted, self
                )

        wizard_embed.description = self.final_text
        wizard_embed.set_footer(text=disnake.Embed.Empty)
        await self.ori_mes.edit(embed=wizard_embed)
