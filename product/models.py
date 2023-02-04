from django.core.validators import MinValueValidator
from django.db import models
from webapp.users.models import User


class Product(models.Model):
    """
    Product model to add a product to the database.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=200, null=True, blank=True)
    sku = models.CharField(max_length=20, unique=True)
    manufacturer = models.CharField(max_length=255, null=True, blank=True)
    quantity = models.IntegerField(default=0, validators=[MinValueValidator(0)])

    class Meta:
        db_table = 'product'
