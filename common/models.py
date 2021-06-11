from piccolo.columns import BigInt
from piccolo.columns import Decimal
from piccolo.columns import Integer
from piccolo.table import Table


class UserInteraction(Table):
    id = Integer(primary=True, key=True)
    user_id = BigInt()
    interactions = Decimal(digits=(4, 1))
