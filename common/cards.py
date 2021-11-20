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
    def display_status(self):
        return self.status.name if self.status != Status.HOST else "ALIVE"

    async def as_embed(self, bot: discord.Client):
        member = await bot.fetch_user(
            self.user_id
        )  # we're assuming this will never fail because i double check everything
        embed = discord.Embed(
            title=self.title_name,
            description=f"By: {member.mention} ({str(member)})\nStatus: **{self.display_status}**",
        )
        embed.set_image(url=self.card_url)
        embed.color = self.status.value

        return embed


talia_card = Card(
    user_id=229350299909881876,
    oc_name="Talia Aelius",
    oc_talent="Online Advertiser",
    card_url="https://cdn.discordapp.com/attachments/457939628209602560/883163389499691089/TaliaAeliusCard.png",
    status=Status.ALIVE,
)
drake_card = Card(
    user_id=229350299909881876,
    oc_name="Drake Aelius",
    oc_talent="Youtuber",
    card_url="https://cdn.discordapp.com/attachments/457939628209602560/883163375272624138/DrakeAeliusCard.png",
    status=Status.HOST,
)
chichi_card = Card(
    user_id=588749122643951616,
    oc_name="Chichi Hanamura",
    oc_talent="Idol",
    card_url="https://cdn.discordapp.com/attachments/457939628209602560/884562807520116766/ChichiHanamuraCard.png",
    status=Status.DEAD,
)
antomy_card = Card(
    user_id=328149026266677248,
    oc_name="Antomy Ideris-Sanjuroku",
    oc_talent="Domestic Helper",
    card_url="https://cdn.discordapp.com/attachments/457939628209602560/884562762435543050/AntomyIderisSanjurokuCard.png",
    status=Status.HOST,
)
hosts = [drake_card, chichi_card, antomy_card]


# alice_card = Card(
#     user_id=422447246060158996,
#     oc_name="Alice Betterman",
#     oc_talent="Humanitarian",
#     card_url="https://cdn.discordapp.com/attachments/457939628209602560/883164203756699748/AliceBettermanCard.png",
# )
cheshire_card = Card(
    user_id=328149026266677248,
    oc_name="Cheshire Cat",
    oc_talent="Stage Magician",
    card_url="https://cdn.discordapp.com/attachments/457939628209602560/883164204994019348/CheshireCatCard.png",
    status=Status.DEAD,
)
chunyu_card = Card(
    user_id=486291559617134592,
    oc_name="Chunyu Tsuguri",
    oc_talent="Surgeon",
    card_url="https://cdn.discordapp.com/attachments/457939628209602560/883830062925885491/ChunyuTsuguriCard.png",
    status=Status.DEAD,
)
codex_card = Card(
    user_id=397994270226907136,
    oc_name="Codex Lemegeton",
    oc_talent="Archivist",
    card_url="https://cdn.discordapp.com/attachments/457939628209602560/883164212443107398/CodexLemegetonCard.png",
)
error_card = Card(
    user_id=463875652718821377,
    oc_name="ERROR",
    oc_talent="???",
    card_url="https://cdn.discordapp.com/attachments/457939628209602560/883830081405976656/ERRORCard.png",
)
fusanosuke_card = Card(
    user_id=248410976808992768,
    oc_name="Fusanosuke Fukushima",
    oc_talent="Performer",
    card_url="https://cdn.discordapp.com/attachments/457939628209602560/883164243455787038/FusanosukeFukushimaCard.png",
    status=Status.DEAD,
)
haru_card = Card(
    user_id=486181655837671425,
    oc_name="Haru Daguchi",
    oc_talent="Parkourist",
    card_url="https://cdn.discordapp.com/attachments/457939628209602560/887481915622436864/HaruDaguchiCard.png",
)
jack_card = Card(
    user_id=206616227588734983,
    oc_name="Jack Rylie",
    oc_talent="Barista",
    card_url="https://cdn.discordapp.com/attachments/457939628209602560/888876861621411840/JackRylieCard.png",
)
josh_card = Card(
    user_id=269156561320935426,
    oc_name="Josh Soha",
    oc_talent="Air Guitarist",
    card_url="https://cdn.discordapp.com/attachments/457939628209602560/883164255678005279/JoshSohaCard.png",
)
karen_card = Card(
    user_id=466081034887495690,
    oc_name="Karen Mahizuna",
    oc_talent="Sommelier",
    card_url="https://cdn.discordapp.com/attachments/457939628209602560/883164259587076126/KarenMahizunaCard.png",
    status=Status.DEAD,
)
katie_card = Card(
    user_id=469806229716205578,
    oc_name="Katie Cerulean Lockwood",
    oc_talent="Detective",
    card_url="https://cdn.discordapp.com/attachments/457939628209602560/883164263370342450/KatieCeruleanLockwoodCard.png",
    status=Status.DEAD,
)
# kyren_card = Card(
#     user_id=103912095455653888,
#     oc_name="Kyren Shinyo",
#     oc_talent="Philologist",
#     card_url="https://cdn.discordapp.com/attachments/457939628209602560/883164267120046110/KyrenShinyoCard.png",
# )
leo_card = Card(
    user_id=191313641943859202,
    oc_name="Leo Kobayashi",
    oc_talent="Film-Video Editor",
    card_url="https://cdn.discordapp.com/attachments/457939628209602560/883164271582785556/LeoKobayashiCard.png",
    status=Status.DEAD,
)
masami_card = Card(
    user_id=578757582186086410,
    oc_name="Masami Okumura",
    oc_talent="Seamstress",
    card_url="https://cdn.discordapp.com/attachments/457939628209602560/883164275756109864/MasamiOkumuraCard.png",
)
# perseus_card = Card(
#     user_id=745908719786655744,
#     oc_name="Perseus Lucien Hyperion",
#     oc_talent="Ballerina",
#     card_url="https://cdn.discordapp.com/attachments/457939628209602560/883164279702970368/PerseusLucienHyperionCard.png",
# )
rui_card = Card(
    user_id=723768708433969243,
    oc_name="Rui Kaida",
    oc_talent="Speedrunner",
    card_url="https://cdn.discordapp.com/attachments/457939628209602560/883164283737899028/RuiKaidaCard.png",
)
shizuru_card = Card(
    user_id=448815258060980226,
    oc_name="Shizuru Naohiro",
    oc_talent="Freerunner",
    card_url="https://cdn.discordapp.com/attachments/457939628209602560/883164297633595442/ShizuruNaohiroCard.png",
)
suri_card = Card(
    user_id=543853525038530561,
    oc_name="Suri Yoshi",
    oc_talent="Pianist",
    card_url="https://cdn.discordapp.com/attachments/457939628209602560/883449952007778365/SuriYoshiCard.png",
)
yakichiro_card = Card(
    user_id=190242058471079936,
    oc_name="Yakichiro Toshio Ochi",
    oc_talent="Hotel Manager",
    card_url="https://cdn.discordapp.com/attachments/457939628209602560/883164330965733426/YakichiroToshioOchiCard.png",
    status=Status.DEAD,
)
yui_card = Card(
    user_id=332568615390019604,
    oc_name="Yui Sakura",
    oc_talent="Hair Model",
    card_url="https://cdn.discordapp.com/attachments/457939628209602560/883164334124073010/YuiSakuraCard.png",
    status=Status.DEAD,
)
zoe_card = Card(
    user_id=475324575815565332,
    oc_name="Zoë Roxanne Taiga",
    oc_talent="Cinematographer",
    card_url="https://cdn.discordapp.com/attachments/457939628209602560/887068688149250108/ZoeRoxanneTaigaCard.png",
    status=Status.DEAD,
)
yanna_card = Card(
    user_id=479102814594007040,
    oc_name="Yanna Akina",
    oc_talent="Journalist",
    card_url="https://cdn.discordapp.com/attachments/457939628209602560/888209703010705459/YannaAkinaCard.png",
    status=Status.DEAD,
)
evelyn_card = Card(
    user_id=293549819828633600,
    oc_name="Evelyn Tsukiki",
    oc_talent="Lullaby Author",
    card_url="https://cdn.discordapp.com/attachments/457939628209602560/888209047902384148/EvelynTsukikiCard.png",
    status=Status.DEAD,
)


participants = [
    # alice_card,
    cheshire_card,
    chunyu_card,
    codex_card,
    error_card,
    fusanosuke_card,
    haru_card,
    jack_card,
    josh_card,
    karen_card,
    katie_card,
    # kyren_card,
    leo_card,
    masami_card,
    # perseus_card,
    rui_card,
    shizuru_card,
    suri_card,
    yakichiro_card,
    yui_card,
    zoe_card,
    yanna_card,
    evelyn_card,
    talia_card,
]
participants.sort(key=lambda card: card.oc_name)
