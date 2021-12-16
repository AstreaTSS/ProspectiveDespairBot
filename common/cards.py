import os
import ssl
import typing
import urllib.request
from dataclasses import dataclass
from enum import Enum

import disnake
import rtoml


class Status(Enum):
    ALIVE = disnake.Color.teal()
    DEAD = disnake.Color.red()
    ESCAPED = disnake.Color.lighter_gray()
    HOST = disnake.Color.darker_gray()


@dataclass
class Card:
    user_id: int
    oc_name: str
    oc_talent: str
    card_url: str
    pronouns: str
    status: Status = Status.ALIVE

    @property
    def mention(self):
        return f"<@{self.user_id}>"

    @property
    def title_name(self):
        return f"{self.oc_name}, the Ultimate {self.oc_talent}"

    @property
    def display_status(self):
        return self.status.name if self.status != Status.HOST else "ALIVE"

    async def as_embed(self, bot: disnake.Client):
        member = await bot.fetch_user(
            self.user_id
        )  # we're assuming this will never fail because i double check everything

        desc = [
            f"**OC By:** {member.mention} ({member})",
            f"**Pronouns:** {self.pronouns}",
            f"**Status:** {self.display_status.title()}",
        ]

        embed = disnake.Embed(title=self.title_name, description="\n".join(desc))

        embed.set_image(url=self.card_url)
        embed.color = self.status.value

        return embed


hosts = []

participants: typing.List[Card] = []
cards_url: typing.Optional[str] = os.environ.get("CARD_FILE_URL")
if cards_url:
    req = urllib.request.Request(
        cards_url,
        headers={"Cache-Control": "no-cache", "Pragma": "no-cache"},
        method="GET",
    )

    # black magic to fix ssl issues on windows
    # https://stackoverflow.com/questions/44629631/while-using-pandas-got-error-urlopen-error-ssl-certificate-verify-failed-cert
    ssl._create_default_https_context = ssl._create_unverified_context

    # forgive me, cus im about to block
    # suggesting how critical these cards are, id say its worth it
    with urllib.request.urlopen(cards_url, timeout=1) as response:
        data = response.read().decode("utf-8")
        cards_dict = rtoml.load(data)

        for card_data in cards_dict["cards"]:
            participants.append(
                Card(
                    card_data["user_id"],
                    card_data["oc_name"],
                    card_data["oc_talent"],
                    card_data["card_url"],
                    card_data["pronouns"],
                    Status[card_data["status"]],
                )
            )

    participants.sort(key=lambda card: card.oc_name)
