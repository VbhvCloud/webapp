import datetime
import uuid

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from webapp.users.models import User


class BaseModel(models.Model):
    """A base model to deal with all the abstract level model creations"""

    class Meta:
        abstract = True

    date_added = models.DateTimeField(auto_now_add=True, editable=False)
    date_last_updated = models.DateTimeField(auto_now=True)

    def get_seconds_since_creation(self):
        """
        Find how much time has been elapsed since creation, in seconds.
        This function is timezone agnostic, meaning this will work even if
        you have specified a timezone.
        """
        return (datetime.datetime.utcnow() -
                self.date_added.replace(tzinfo=None)).seconds


class Product(BaseModel):
    """
    Product model to add a product to the database.
    """

    owner_user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
    sku = models.CharField(max_length=20, unique=True)
    manufacturer = models.CharField(max_length=255)
    quantity = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])

    class Meta:
        db_table = 'product'


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image_id = models.AutoField(primary_key=True, editable=False)
    file_name = models.CharField(max_length=200, editable=False)
    date_created = models.DateTimeField(auto_now_add=True, editable=False)
    s3_bucket_path = models.CharField(max_length=200, null=True, editable=False)
