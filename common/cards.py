from dataclasses import dataclass
from enum import Enum

import discord


class Status(Enum):
    ALIVE = discord.Color.teal()
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

    @property
    def mention(self):
        return f"<@{self.user_id}>"

    @property
    def title_name(self):
        return f"{self.oc_name}, the Ultimate {self.oc_talent}"

    @property
    def get_status(self):
        return self.status.name if self.status != Status.HOST else "ALIVE"

    async def as_embed(self, bot: discord.Client):
        member = await bot.fetch_user(
            self.user_id
        )  # we're assuming this will never fail because i double check everything
        embed = discord.Embed(
            title=self.title_name,
            description=f"By: {member.mention} ({str(member)})\nStatus: **{self.get_status}**",
        )
        embed.set_image(url=self.card_url)
        embed.color = self.status.value

        return embed

hosts = []


# order of these cards do not represent anything whatsoever
# (well, okay, for dh, they're somewhat by alphabet, though not entirely)
# they're just like that
# everything gets sorted by oc name anyways
aaron_card = Card(
    user_id=673944515417079847,
    oc_name="Aaron Ovengue",
    oc_talent="Gang Leader",
    card_url="https://cdn.discordapp.com/attachments/457939628209602560/861074575131672616/AaronOvengueCard.png",
    status=Status.DEAD,
)
adrian_card = Card(
    user_id=496893333277376514,
    oc_name="Adrian Shpion",
    oc_talent="???",
    card_url="https://cdn.discordapp.com/attachments/457939628209602560/861074580843135006/AdrianShpionCard.png",
    status=Status.DEAD,
)
auko_card = Card(
    user_id=447899165373235200,
    oc_name="Auko Corbyn",
    oc_talent="Astronomer",
    card_url="https://cdn.discordapp.com/attachments/457939628209602560/861074581624324096/AukoCorbynCard.png",
)
ayaka_card = Card(
    user_id=284589540553916416,
    oc_name="Ayaka Sato",
    oc_talent="Pastry Chef",
    card_url="https://cdn.discordapp.com/attachments/457939628209602560/861074581996568626/AyakaSatoCard.png",
)
hoshi_card = Card(
    user_id=229350299909881876,
    oc_name="Hoshi Corbyn",
    oc_talent="Ufologist",
    card_url="https://cdn.discordapp.com/attachments/457939628209602560/861074582227910696/HoshiCorbynCard.png",
    status=Status.DEAD,
)
inultes_card = Card(
    user_id=339972906693951489,
    oc_name="Inultes Fouvate",
    oc_talent="Animal Tamer",
    card_url="https://cdn.discordapp.com/attachments/457939628209602560/861074583007264798/InultesFouvateCard.png",
)
itochan_card = Card(
    user_id=403962675270516737,
    oc_name="Ito-Chan",
    oc_talent="Kids Show Host",
    card_url="https://cdn.discordapp.com/attachments/457939628209602560/861074584530059314/ItoChanCard.png",
)
kokoa_card = Card(
    user_id=282655798692282368,
    oc_name="Kokoa Morinaga",
    oc_talent="Chocolatier",
    card_url="https://cdn.discordapp.com/attachments/457939628209602560/861074586014842930/KokoaMorinagaCard.png",
)
konda_card = Card(
    user_id=454331602831671296,
    oc_name="Konda Sho",
    oc_talent="Hunter",
    card_url="https://cdn.discordapp.com/attachments/457939628209602560/861074587991277578/KondaShoCard.png",
)
kuno_card = Card(
    user_id=623152586182098964,
    oc_name="Kuno Taikan",
    oc_talent="Conspiracy Theorist",
    card_url="https://cdn.discordapp.com/attachments/457939628209602560/861074589039722506/KunoTaikanCard.png",
    status=Status.DEAD,
)
midas_card = Card(
    user_id=422447246060158996,
    oc_name="Midas Edric",
    oc_talent="Prankster",
    card_url="https://cdn.discordapp.com/attachments/457939628209602560/861074692370202635/MidasEdricCard.png",
    status=Status.DEAD,
)
mikhail_card = Card(
    user_id=314934503913160704,
    oc_name="Mikhail Dmitrievich Kirillov",
    oc_talent="Violist",
    card_url="https://cdn.discordapp.com/attachments/457939628209602560/863866034000101386/MikhailDmitrievichKirillovCard.png",
    status=Status.DEAD,
)
nine_card = Card(
    user_id=448815258060980226,
    oc_name="Nine",
    oc_talent="Origamist",
    card_url="https://cdn.discordapp.com/attachments/457939628209602560/861074737023549480/NineCard.png",
)
paolo_card = Card(
    user_id=220274643401965578,
    oc_name="Paolo Donini",
    oc_talent="Racer",
    card_url="https://cdn.discordapp.com/attachments/457939628209602560/861074740923203594/PaoloDoniniCard.png",
    status=Status.DEAD,
)
pluviam_card = Card(
    user_id=475792369023713291,
    oc_name="Pluviam Lone",
    oc_talent="Mortician",
    card_url="https://cdn.discordapp.com/attachments/457939628209602560/861074744757190667/PluviamLoneCard.png",
    status=Status.DEAD,
)
ryuunosuke_card = Card(
    user_id=226178585227034624,
    oc_name="Ryuunosuke Edahiko",
    oc_talent="Actor",
    card_url="https://cdn.discordapp.com/attachments/457939628209602560/861074748602581033/RyuunosukeEdahikoCard.png",
    status=Status.DEAD,
)
sayaka_card = Card(
    user_id=328149026266677248,
    oc_name="Sayaka Taira",
    oc_talent="Sleuth",
    card_url="https://cdn.discordapp.com/attachments/457939628209602560/861074752420184074/SayakaTairaCard.png",
)
sierra_card = Card(
    user_id=588749122643951616,
    oc_name="Sierra Mistaria",
    oc_talent="Fashion Designer",
    card_url="https://cdn.discordapp.com/attachments/457939628209602560/861074756160454656/SierraMistariaCard.png",
    status=Status.DEAD,
)
spike_card = Card(
    user_id=303254061644382219,
    oc_name="Spike Guns",
    oc_talent="Greaser",
    card_url="https://cdn.discordapp.com/attachments/457939628209602560/861074760784150528/SpikeGunsCard.png",
)
toru_card = Card(
    user_id=612332658340528130,
    oc_name="Toru Kurou",
    oc_talent="Internet Troll",
    card_url="https://cdn.discordapp.com/attachments/457939628209602560/861074786607431680/ToruKurouCard.png",
)
veyel_card = Card(
    user_id=387610935122067456,
    oc_name="Veyel Thoumeaux",
    oc_talent="Cleaner",
    card_url="https://cdn.discordapp.com/attachments/457939628209602560/861074791347388436/VeyelThoumeauxCard.png",
    status=Status.DEAD,
)
yuko_card = Card(
    user_id=486181655837671425,
    oc_name="Yuko Aikawa",
    oc_talent="Shrine Maiden",
    card_url="https://cdn.discordapp.com/attachments/457939628209602560/861074810581811211/YukoAikawaCard.png",
)


participants = [
    aaron_card,
    adrian_card,
    auko_card,
    ayaka_card,
    hoshi_card,
    inultes_card,
    itochan_card,
    kokoa_card,
    konda_card,
    kuno_card,
    midas_card,
    mikhail_card,
    nine_card,
    paolo_card,
    pluviam_card,
    ryuunosuke_card,
    sayaka_card,
    sierra_card,
    spike_card,
    toru_card,
    veyel_card,
    yuko_card
]
participants.sort(key=lambda card: card.oc_name)
