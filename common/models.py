import typing
from decimal import Decimal

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
