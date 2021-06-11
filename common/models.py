import databases
import ormar
import sqlalchemy

DATABASE_URL = "sqlite:///db.sqlite3"
database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()


class BaseMeta(ormar.ModelMeta):
    metadata = metadata
    database = database


class UserInteraction(ormar.Model):
    class Meta(BaseMeta):
        tablename = "user_interaction"

    id: int = ormar.Integer(primary_key=True, unique=True, autoincrement=True)
    user_id: int = ormar.BigInteger()
    interactions: str = ormar.String(max_length=40)
