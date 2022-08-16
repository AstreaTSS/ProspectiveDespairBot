import os
import ssl
import typing
import urllib.request
from enum import Enum
from enum import IntEnum

import attrs
import naff
import tomli


class Status(Enum):
    ALIVE = naff.Color(0xFFC0FC)
    DEAD = naff.Color(0xE74C3C)
    ESCAPED = naff.Color(0x95A5A6)
    HOST = naff.Color(0x546E7A)


class Artist(IntEnum):
    CILANTRO = 426951636490125321
    CURDS = 463875652718821377
    SAGA = 475324575815565332


@attrs.define()
class Card:
    user_id: int
    oc_name: str
    oc_talent: str
    artist: Artist
    card_url: str
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

    async def as_embed(self, bot: naff.Client):
        user: naff.User = await bot.fetch_user(self.user_id)  # type: ignore
        artist: naff.User = await bot.fetch_user(self.artist.value)  # type: ignore

        desc = [
            f"**OC By:** {user.mention} ({user.tag})",
            f"**Drawn By:** {artist.mention} ({artist.tag})",
            f"**Status:** {self.display_status}",
        ]

        embed = naff.Embed(title=self.title_name, description="\n".join(desc))

        embed.set_image(url=self.card_url)
        embed.color = self.status.value

        return embed


# black magic to fix ssl issues
# https://stackoverflow.com/questions/44629631/while-using-pandas-got-error-urlopen-error-ssl-certificate-verify-failed-cert
ssl._create_default_https_context = ssl._create_unverified_context

hosts: typing.List[Card] = [
    Card(
        user_id=229350299909881876,
        oc_name="Mayumi Takimura",
        oc_talent="Tennis Player",
        artist=Artist.SAGA,
        card_url="https://cdn.discordapp.com/attachments/968999545621078089/1006651564716474419/MayumiTakimuraCard.png",
        status=Status.HOST,
    ),
    Card(
        user_id=328149026266677248,
        oc_name="Pika Churu",
        oc_talent="Ultimate Collector",
        artist=Artist.SAGA,
        card_url="https://cdn.discordapp.com/attachments/968999545621078089/1008564467375804446/PikaChuruCard.png",
        status=Status.HOST,
    ),
    Card(
        user_id=588749122643951616,
        oc_name="Madelyn Connor",
        oc_talent="Impersonator",
        artist=Artist.CILANTRO,
        card_url="https://cdn.discordapp.com/attachments/968999545621078089/1008923493750014022/MadelynConnorCard.png",
        status=Status.HOST,
    ),
]

participants: typing.List[Card] = []
cards_url: typing.Optional[str] = os.environ.get("CARD_FILE_URL")
if cards_url:
    req = urllib.request.Request(
        cards_url,
        headers={"Cache-Control": "no-cache", "Pragma": "no-cache"},
        method="GET",
    )

    # forgive me, cus im about to block
    # suggesting how critical these cards are, id say its worth it
    with urllib.request.urlopen(cards_url, timeout=1) as response:
        data = response.read().decode("utf-8")
        cards_dict = tomli.loads(data)

        for card_data in cards_dict["cards"]:
            participants.append(
                Card(
                    card_data["user_id"],
                    card_data["oc_name"],
                    card_data["oc_talent"],
                    Artist[card_data["artist"].upper()],
                    card_data["card_url"],
                    Status[card_data["status"]],
                )
            )

    participants.sort(key=lambda card: card.oc_name)
