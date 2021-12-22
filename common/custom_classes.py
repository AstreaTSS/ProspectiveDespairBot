#!/usr/bin/env python3.8
import asyncio
import typing

import attr
import disnake
from disnake.ext import commands

import common.utils as utils


@attr.s(slots=True, init=False)
class SelectionPrompt:
    ctx: typing.Union[
        commands.Context[commands.Bot], disnake.ApplicationCommandInteraction
    ] = attr.ib()
    entries: typing.List[typing.Any] = attr.ib()
    ephemeral: bool = attr.ib()

    view: disnake.ui.View = attr.ib()
    stop: asyncio.Event = attr.ib()
    value: typing.Optional[str] = attr.ib()

    def __init__(
        self,
        ctx: typing.Union[commands.Context, disnake.ApplicationCommandInteraction],
        entries: typing.List[typing.Any],
        ephemeral: bool = False,
    ):
        self.ctx = ctx
        self.entries = entries
        self.ephemeral = ephemeral

        self.value = None
        self.stop = asyncio.Event()
        self.view = self.create_select()

    def create_select(self):
        ori_self = self

        class Selector(disnake.ui.Select):
            def __init__(self, entries: typing.List[typing.Any]):
                options = [disnake.SelectOption(label=str(e)) for e in entries]

                super().__init__(
                    placeholder="Choose an option:",
                    min_values=1,
                    max_values=1,
                    options=options,
                )

            async def callback(self, inter: disnake.MessageInteraction):
                ori_self.value = inter.values[0]
                ori_self.stop.set()

        class SelectorView(disnake.ui.View):
            def __init__(self, entries: typing.List[typing.Any]):
                super().__init__(timeout=10)

                self.add_item(Selector(entries))

            async def interaction_check(
                self, inter: disnake.MessageInteraction
            ) -> bool:
                return ori_self.ctx.author == inter.user

            async def on_timeout(self) -> None:
                ori_self.stop.set()

        return SelectorView(self.entries)

    async def run(self):
        embed = disnake.Embed(
            color=self.ctx.bot.color,
            description="Multiple options detected. Please select an option.",
        )

        mes: typing.Union[
            disnake.Message, disnake.WebhookMessage, disnake.InteractionMessage, None
        ] = None

        if isinstance(self.ctx, commands.Context):
            mes = await self.ctx.reply(embed=embed, view=self.view)
        else:
            if self.ctx.response.is_done():
                mes = await self.ctx.followup.send(
                    embed=embed, view=self.view, ephemeral=self.ephemeral, wait=True
                )
            else:
                await self.ctx.response.send_message(
                    embed=embed, view=self.view, ephemeral=self.ephemeral
                )
                try:
                    mes = await self.ctx.original_message()
                except disnake.HTTPException:
                    pass

        await self.stop.wait()
        if mes:
            try:
                await mes.delete()
            except disnake.HTTPException:
                pass

        return self.value


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
