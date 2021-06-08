# use this to generate db if you need to
from tortoise import run_async
from tortoise import Tortoise

import common.cards
import common.models


async def init():
    await Tortoise.init(
        db_url="sqlite://db.sqlite3", modules={"models": ["common.models"]}
    )
    await Tortoise.generate_schemas()

    user_ids = tuple(c.user_id for c in common.cards.participants)

    for id in user_ids:
        await common.models.UserInteraction.create(user_id=id, interactions=0)


run_async(init())
