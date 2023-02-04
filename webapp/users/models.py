# Python imports
import datetime

# Django Imports
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.core.validators import MinValueValidator
from django.db import models

# Project Imports
from .managers import UserManager


class BaseModel(models.Model):
    """A base model to deal with all the abstract level model creations"""

    class Meta:
        abstract = True

    account_created = models.DateTimeField(auto_now_add=True, editable=False)
    account_updated = models.DateTimeField(auto_now=True)

    def get_seconds_since_creation(self):
        """
        Find how much time has been elapsed since creation, in seconds.
        This function is timezone agnostic, meaning this will work even if
        you have specified a timezone.
        """
        return (datetime.datetime.utcnow() -
                self.account_created.replace(tzinfo=None)).seconds


class User(BaseModel, AbstractBaseUser, PermissionsMixin):
    """
    Default custom user model for webapp.
    If adding fields that need to be filled at user signup,
    check forms.SignupForm and forms.SocialSignupForms accordingly.
    """

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=150, unique=True)
    password = models.CharField(max_length=255)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()
