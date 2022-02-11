import typing
from decimal import Decimal
from email.policy import default

from tortoise import fields
from tortoise.models import Model


class UserInteraction(Model):
    class Meta:
        table = "pduserinteraction"

    id: int = fields.IntField(pk=True)
    user_id: int = fields.BigIntField()
    interactions: Decimal = fields.DecimalField(4, 2)
    total_interactions: Decimal = fields.DecimalField(7, 2)


class MovementEntry(Model):
    class Meta:
        table = "pdmovemententry"

    id: int = fields.IntField(pk=True)
    entry_channel_id: int = fields.BigIntField()
    dest_channel_id: int = fields.BigIntField()
    user_id: typing.Optional[int] = fields.BigIntField(null=True, default=None)


class MiniKGPoints(Model):
    class Meta:
        table = "pdminikgpoints"

    user_id: int = fields.BigIntField(pk=True)
    points: Decimal = fields.DecimalField(5, 2)
    rollover_points: Decimal = fields.DecimalField(5, 2, default=0)
    in_game: bool = fields.BooleanField(default=True)  # type: ignore
