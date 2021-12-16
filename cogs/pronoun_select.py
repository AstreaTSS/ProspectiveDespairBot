import importlib

import disnake
from disnake.ext import commands

import common.utils as utils


class PronounDropdown(disnake.ui.Select):
    def __init__(self):
        self.pronoun_roles = set(
            (
                disnake.Object(879921959176126464),
                disnake.Object(879925849871224873),
                disnake.Object(879921936480743454),
                disnake.Object(879921972614660207),
                disnake.Object(879922010141118464),
                disnake.Object(879921990599847977),
                disnake.Object(879926017236553749),
            )
        )

        options = [
            disnake.SelectOption(
                label="She/her", value="pdpronoun:879921959176126464|She/her"
            ),
            disnake.SelectOption(
                label="It/its", value="pdpronoun:879925849871224873|It/its"
            ),
            disnake.SelectOption(
                label="He/him", value="pdpronoun:879921936480743454|He/him"
            ),
            disnake.SelectOption(
                label="They/them", value="pdpronoun:879921972614660207|They/them"
            ),
            disnake.SelectOption(
                label="Neopronouns", value="pdpronoun:879922010141118464|Neopronouns"
            ),
            disnake.SelectOption(
                label="Any Pronouns", value="pdpronoun:879921990599847977|Any Pronouns"
            ),
            disnake.SelectOption(
                label="Ask for Pronouns",
                value="pdpronoun:879926017236553749|Ask for Pronouns",
            ),
        ]

        super().__init__(
            custom_id="pdpronounselect",
            placeholder="Select your pronouns!",
            min_values=0,
            max_values=7,
            options=options,
        )

    async def callback(self, inter: disnake.Interaction):
        member = inter.user

        if not isinstance(member, disnake.Member):
            await inter.send("An error occured. Please try again.", ephemeral=True)
            return

        # do this weirdness since doing member.roles has a cache
        # search cost which can be expensive if there are tons of roles
        member_roles = {disnake.Object(r) for r in member._roles}
        member_roles.difference_update(self.pronoun_roles)

        if self.values:
            add_list = []

            for values in self.values:
                split_string = values.split("pdpronoun:")[1].split("|")
                pronoun_role = disnake.Object(split_string[0])
                pronoun_name = split_string[1]

                member_roles.add(pronoun_role)
                add_list.append(f"`{pronoun_name}`")

            await member.edit(roles=list(member_roles))
            await inter.response.send_message(
                "New Pronouns: " + ", ".join(add_list), ephemeral=True
            )

        else:
            await member.edit(roles=list(member_roles))
            await inter.response.send_message("All pronouns removed.", ephemeral=True)


class PronounDropdownView(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

        self.add_item(PronounDropdown())


class PronounSelect(commands.Cog, name="Pronoun Select"):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

        if not self.bot.added_pronoun_view:
            self.bot.add_view(PronounDropdownView())
            self.bot.added_pronoun_view = True

    @commands.command()
    @utils.proper_permissions()
    async def send_pronoun_select(self, ctx: commands.Context):
        str_builder = [
            "**Role Menu: Pronouns**",
            "Select the pronouns you wish to have.",
            "Any old pronouns not re-selected will be removed.",
        ]

        await ctx.send("\n".join(str_builder), view=PronounDropdownView())
        await ctx.message.delete()


def setup(bot):
    importlib.reload(utils)
    bot.add_cog(PronounSelect(bot))
