import importlib

import disnake
from disnake.ext import commands

import common.utils as utils


class CountingPinCMDs(commands.Cog, name="Pinboard"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def _generate_embed(self, msg: disnake.Message):
        # so here's where we try to replicate seraphim's pins
        send_embed = disnake.Embed(description=msg.content, timestamp=msg.created_at)
        send_embed.colour = disnake.Colour.default()
        send_embed.set_author(
            name=f"{msg.author.display_name} ({str(msg.author)})",
            icon_url=utils.get_icon_url(msg.author.display_avatar),
        )
        send_embed.set_footer(text=f"ID: {msg.id}")
        send_embed.add_field(
            name="Original", value=f"[Jump]({msg.jump_url})", inline=True
        )
        return send_embed

    @commands.Cog.listener()
    async def on_message(self, msg: disnake.Message):
        if (
            msg.type != disnake.MessageType.pins_add
            or not msg.guild
            or msg.channel.id != 675038247197343752
        ):
            return

        pins = await msg.channel.pins()

        if len(pins) > 0:
            entry = pins[-1]
            des_chan = msg.guild.get_channel(718507357386178560)
            if des_chan is None:
                return

            send_embed = self._generate_embed(entry)
            await des_chan.send(embed=send_embed)
            await entry.unpin()

    @commands.command(aliases=["pin_all"])
    @utils.proper_permissions()
    async def pinall(self, ctx: commands.Context):
        """
        Retroactively moves overflowing pins from the counting channel to the destination channel.
        Requires Manage Server permissions or higher.
        """

        if not ctx.guild:
            raise commands.BadArgument("This isn't being run in the server!")

        ori_chan: disnake.TextChannel = ctx.guild.get_channel(675038247197343752)

        pins = await ori_chan.pins()
        pins.reverse()  # pins are retrived newest -> oldest, we want to do the opposite

        if len(pins) <= 0:
            raise utils.CustomCheckFailure(
                "The number of pins is below or at the limit!"
            )

        des_chan = ctx.guild.get_channel(718507357386178560)
        if des_chan is None:
            raise utils.CustomCheckFailure(
                "The destination channel doesn't exist anymore! Please fix this."
            )

        dif = len(pins)
        pins_subset = pins[-dif:]
        pins_subset.reverse()

        for pin in pins_subset:
            send_embed = self._generate_embed(pin)
            await des_chan.send(embed=send_embed)
            await pin.unpin()

        await ctx.reply("Done!")


def setup(bot):
    importlib.reload(utils)
    bot.add_cog(CountingPinCMDs(bot))
