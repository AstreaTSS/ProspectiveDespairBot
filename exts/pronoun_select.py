import importlib

import naff

import common.utils as utils


class PronounSelect(utils.Extension):
    def __init__(self, bot):
        self.bot: naff.Client = bot
        self.name = "Pronoun Select"

        self.pronoun_select = naff.Select(
            options=[
                naff.SelectOption(
                    label="She/her", value="pdpronoun:879921959176126464|She/her"
                ),
                naff.SelectOption(
                    label="It/its", value="pdpronoun:879925849871224873|It/its"
                ),
                naff.SelectOption(
                    label="He/him", value="pdpronoun:879921936480743454|He/him"
                ),
                naff.SelectOption(
                    label="They/them", value="pdpronoun:879921972614660207|They/them"
                ),
                naff.SelectOption(
                    label="Neopronouns",
                    value="pdpronoun:879922010141118464|Neopronouns",
                ),
                naff.SelectOption(
                    label="Any Pronouns",
                    value="pdpronoun:879921990599847977|Any Pronouns",
                ),
                naff.SelectOption(
                    label="Ask for Pronouns",
                    value="pdpronoun:879926017236553749|Ask for Pronouns",
                ),
            ],
            custom_id="pdpronounselect",
            placeholder="Select your pronouns!",
            min_values=0,
            max_values=25,
        )

        self.pronoun_roles = {
            879921959176126464,
            879925849871224873,
            879921936480743454,
            879921972614660207,
            879922010141118464,
            879921990599847977,
            879926017236553749,
        }

    @naff.prefixed_command()
    @utils.proper_permissions()
    async def send_pronoun_select(self, ctx: naff.PrefixedContext):
        str_builder = [
            "**Role Menu: Pronouns**",
            "Select the pronouns you wish to have.",
            "Any old pronouns not re-selected will be removed.",
        ]

        await ctx.send("\n".join(str_builder), components=self.pronoun_select)
        await ctx.message.delete()

    @naff.component_callback("pdpronounselect")  # type: ignore
    async def selected_pronoun(self, ctx: naff.ComponentContext):
        member = ctx.author

        if not isinstance(member, naff.Member):
            await ctx.send("An error occured. Please try again.", ephemeral=True)
            return

        # do this weirdness since doing member.roles has a cache
        # search cost which can be expensive if there are tons of roles
        member_roles = {int(r) for r in member._role_ids}
        member_roles.difference_update(self.pronoun_roles)

        if ctx.values:
            add_list = []

            for value in ctx.values:
                value: str
                split_string = value.removeprefix("pdpronoun:").split("|")
                pronoun_role = int(split_string[0])
                pronoun_name = split_string[1]

                member_roles.add(pronoun_role)
                add_list.append(f"`{pronoun_name}`")

            await member.edit(roles=list(member_roles))
            await ctx.send(f"New Pronouns: {', '.join(add_list)}.", ephemeral=True)

        else:
            await member.edit(roles=list(member_roles))
            await ctx.send("All pronouns removed.", ephemeral=True)


def setup(bot):
    importlib.reload(utils)
    PronounSelect(bot)
