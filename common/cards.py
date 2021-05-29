from dataclasses import dataclass
from enum import Enum

import discord


class Status(Enum):
    ALIVE = discord.Color(3062497)
    DEAD = discord.Color.red()
    ESCAPED = discord.Color.lighter_gray()
    HOST = discord.Color.darker_gray()


@dataclass
class Card:
    user_id: int
    oc_name: str
    oc_talent: str
    card_url: str
    status: Status = Status.ALIVE

    def mention(self):
        return f"<@{self.user_id}>"

    def title_name(self):
        return f"{self.oc_name}, the Ultimate {self.oc_talent}"

    async def as_embed(self, bot: discord.Client):
        member = await bot.get_user(
            self.user_id
        )  # we're assuming this will never fail because i double check everything
        embed = discord.Embed(
            title=self.title_name(),
            description=f"By: {member.mention} ({str(member)})\nStatus: **{self.status}**",
        )
        embed.set_image(url=self.card_url)
        embed.color = self.status.value

        return embed


drake_card = Card(
    user_id=229350299909881876,
    oc_name="Drake Aelius",
    oc_talent="Youtuber",
    card_url="https://cdn.discordapp.com/attachments/786719895051304980/818595354416775249/DrakeAeliusCard.png",
    status=Status.HOST
)
hosts = [drake_card]


bat_card = Card(
    user_id=770866874468270092,
    oc_name="Bat Allan-Poe",
    oc_talent="Gothic Horror Writer",
    card_url="https://cdn.discordapp.com/attachments/429720487678050308/848239705463980113/BatAllanPoeCard.png",
)
david_card = Card(
    user_id=723768708433969243,
    oc_name="David Joseph Russell",
    oc_talent="Social Engineer",
    card_url="https://cdn.discordapp.com/attachments/429720487678050308/848239706654244922/DavidJosephRussellCard.png",
)
ema_card = Card(
    user_id=543853525038530561,
    oc_name="Ema Isaru",
    oc_talent="Confectioner",
    card_url="https://cdn.discordapp.com/attachments/429720487678050308/848239711159189534/EmaIsaruCard.png",
)
fausto_card = Card(
    user_id=140543419104755712,
    oc_name="Fausto Rochada",
    oc_talent="Boxer",
    card_url="https://cdn.discordapp.com/attachments/429720487678050308/848239712804274246/FaustoRochadaCard.png",
)
hikaru_card = Card(
    user_id=621631815311949834,
    oc_name="Hikaru",
    oc_talent="Butler",
    card_url="https://cdn.discordapp.com/attachments/429720487678050308/848239715588374568/Hikaru.png",
)
jack_card = Card(
    user_id=269156561320935426,
    oc_name="Jack Enjo",
    oc_talent="Pyrotechnician",
    card_url="https://cdn.discordapp.com/attachments/429720487678050308/848239717081808906/JackEnjoCard.png",
)
jacob_card = Card(
    user_id=295713288585478147,
    oc_name="Jacob Canon",
    oc_talent="Nightcrawler",
    card_url="https://cdn.discordapp.com/attachments/429720487678050308/848239718415728682/JacobCanonCard.png",
)
kento_card = Card(
    user_id=333292261024595969,
    oc_name="Kento Masumi",
    oc_talent="Bass Player",
    card_url="https://cdn.discordapp.com/attachments/429720487678050308/848239748320854046/KentoMasumiCard.png",
)
kojima_card = Card(
    user_id=217419998677696512,
    oc_name="Kojima Akihiro",
    oc_talent="Vlogger",
    card_url="https://cdn.discordapp.com/attachments/429720487678050308/848239753610526770/KojimaAkihiroCard.png",
)
noriko_card = Card(
    user_id=248410976808992768,
    oc_name="Noriko Nakai",
    oc_talent="Cup Stacker",
    card_url="https://cdn.discordapp.com/attachments/429720487678050308/848239779682451506/NorikoNakaiCard.png",
)
rita_card = Card(
    user_id=333099173677105153,
    oc_name="Rita Toscani",
    oc_talent="Fashion Historian",
    card_url="https://cdn.discordapp.com/attachments/429720487678050308/848239782621610044/RitaToscaniCard.png",
)
takuya_card = Card(
    user_id=288772793460457473,
    oc_name="Takuya Erion",
    oc_talent="Operator",
    card_url="https://cdn.discordapp.com/attachments/429720487678050308/848239784576024586/TakuyaErionCard.png",
)
tokumei_card = Card(
    user_id=578326021443420160,
    oc_name="Tokumei Sakkaku",
    oc_talent="War Strategist",
    card_url="https://cdn.discordapp.com/attachments/429720487678050308/848239786925359184/TokumeiSakkakuCard.png",
)

participants = [
    bat_card,
    david_card,
    ema_card,
    fausto_card,
    hikaru_card,
    jack_card,
    jacob_card,
    kento_card,
    kojima_card,
    noriko_card,
    rita_card,
    takuya_card,
    tokumei_card,
]
participants.sort(key=lambda card: card.oc_name)