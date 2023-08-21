from tortoise import models, fields


class User(models.Model):
    """
    User Model
    """
    id = fields.UUIDField(pk=True)
    fullname = fields.CharField(max_length=255)
    email = fields.CharField(max_length=255, unique=True)
    password = fields.CharField(max_length=255)

    def __str__(self):
        return self.fullname

    class PydanticMeta:
        exclude = ['password']
