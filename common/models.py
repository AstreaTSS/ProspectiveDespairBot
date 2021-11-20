from decimal import Decimal

from tortoise import fields
from tortoise.models import Model


class UserInteraction(Model):
    class Meta:
        table = "dhuserinteraction"

    id: int = fields.IntField(pk=True)
    user_id: int = fields.BigIntField()
    interactions: Decimal = fields.DecimalField(4, 2)
    total_interactions: Decimal = fields.DecimalField(7, 2)
