from enum import Enum
from tortoise import models, fields


class PaymentTypes(str, Enum):
    """
    Payment Types Enum
    """
    cash = 'Cash'
    cashless = 'Cashless'


class Receipt(models.Model):
    """
    Receipt Model
    """
    id = fields.UUIDField(pk=True)
    date = fields.DatetimeField(auto_now=True)
    user = fields.ForeignKeyField('models.User', related_name='user')

    products = fields.ManyToManyField('models.Product', related_name='products', through='receiptproduct')
    payment = fields.ForeignKeyField('models.Payment', related_name='payment')
    total = fields.FloatField()
    rest = fields.FloatField()

    def __str__(self):
        return self.id

    class PydanticMeta:
        exclude = ('user', 'user_id', 'products')


class Payment(models.Model):
    """
    Payment method Model
    """
    id = fields.UUIDField(pk=True)
    type = fields.CharEnumField(PaymentTypes)
    amount = fields.FloatField()


class Product(models.Model):
    """
    Product Model
    """
    id = fields.UUIDField(pk=True)
    name = fields.CharField(max_length=255)

    def __str__(self):
        return self.name


class ReceiptProduct(models.Model):
    """
    Many-to-Many Product-Receipt Model with extended data
    """
    id = fields.UUIDField(pk=True)
    receipt = fields.ForeignKeyField("models.Receipt")
    product = fields.ForeignKeyField("models.Product")
    quantity = fields.IntField()
    price = fields.FloatField()

    def total(self) -> float:
        return self.quantity * self.price

    class PydanticMeta:
        computed = ('total',)
