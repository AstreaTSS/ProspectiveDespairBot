from tortoise import fields
from tortoise.models import Model


class UserInteraction(Model):
    class Meta:
        table = "pduserinteraction"

    id = fields.IntField(pk=True)
    user_id = fields.BigIntField()
    interactions = fields.DecimalField(4, 1)
