# use this to generate db if you need to
import os

from tortoise import run_async
from tortoise import Tortoise


async def init():
    await Tortoise.init(
        db_url=os.environ.get("DB_URL"), modules={"models": ["common.models"]}
    )
    await Tortoise.generate_schemas()


run_async(init())
