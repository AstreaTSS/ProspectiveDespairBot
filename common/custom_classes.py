import asyncio
import contextlib
import typing

import attrs
import naff


class Typing:
    """A port of discord.py's typing context manager."""

    def __init__(self, channel: naff.MessageableMixin) -> None:
        self.channel = channel
        self.loop: asyncio.AbstractEventLoop = asyncio.get_running_loop()

    def _typing_done_callback(self, fut: asyncio.Future) -> None:
        with contextlib.suppress(asyncio.CancelledError, Exception):
            fut.exception()

    async def do_typing(self) -> None:
        while True:
            await asyncio.sleep(5)
            await self.channel.trigger_typing()

    async def __aenter__(self) -> None:
        await self.channel.trigger_typing()
        self.task: asyncio.Task[None] = self.loop.create_task(self.do_typing())
        self.task.add_done_callback(self._typing_done_callback)

    async def __aexit__(
        self,
        exc_type,
        exc,
        traceback,
    ) -> None:
        self.task.cancel()


@attrs.define()
class WizardQuestion:
    question: str = attrs.field()
    converter: typing.Callable = attrs.field()
    action: typing.Callable = attrs.field()


@attrs.define(slots=False)
class WizardManager:
    """A class that allows you to make a wizard of sorts, allowing a more intuitive way of getting multiple inputs from a user."""

    embed_title: str = attrs.field()
    final_text: str = attrs.field()
    color: naff.Color = attrs.field(default=naff.Color(0x2EBAE1))
    timeout: float = attrs.field(default=120)
    pass_self: bool = attrs.field(default=False)

    questions: typing.List[WizardQuestion] = attrs.field(factory=list, init=False)
    ori_mes: typing.Optional[naff.Message] = attrs.field(default=None, init=False)

    def add_question(
        self, question: str, converter: typing.Callable, action: typing.Callable
    ):
        self.questions.append(WizardQuestion(question, converter, action))

    async def run(self, ctx: naff.PrefixedContext):
        def check(e: naff.events.MessageCreate):
            m = e.message
            return m.author == ctx.author and m.channel == ctx.channel

        wizard_embed = naff.Embed(title=self.embed_title, color=self.color)
        wizard_embed.set_author(
            name=f"{ctx.bot.user.username}", icon_url=ctx.guild.me.display_avatar.url
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
                reply_event: naff.events.MessageCreate = await ctx.bot.wait_for(
                    "message_create", checks=check, timeout=self.timeout
                )
                reply = reply_event.message
            except asyncio.TimeoutError:
                wizard_embed.description = "Failed to reply. Exiting..."
                wizard_embed.footer = None
                await self.ori_mes.edit(embed=wizard_embed)
                return
            else:
                if reply.content.lower() == "exit":
                    wizard_embed.description = "Exiting..."
                    wizard_embed.footer = None
                    await self.ori_mes.edit(embed=wizard_embed)
                    return

            try:
                converted = await naff.utils.maybe_coroutine(
                    question.converter, ctx, reply.content
                )
            except Exception as e:  # base exceptions really shouldn't be caught
                wizard_embed.description = (
                    f"Invalid input. Exiting...\n\nError: {str(e)}"
                )
                wizard_embed.footer = None
                await self.ori_mes.edit(embed=wizard_embed)
                return

            if not self.pass_self:
                await naff.utils.maybe_coroutine(question.action, ctx, converted)
            else:
                await naff.utils.maybe_coroutine(
                    question.action,
                    self,
                    ctx,
                    converted,
                )

        wizard_embed.description = self.final_text
        wizard_embed.footer = None
        await self.ori_mes.edit(embed=wizard_embed)
