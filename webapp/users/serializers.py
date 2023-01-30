# Django imports
from django.contrib.auth.hashers import make_password

# Rest framework imports
from rest_framework import serializers

# Project imports
from .models import User


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', "last_name", "email", "password"]

    @staticmethod
    def validate_password(password) -> str:
        """ A function to save the password for storing the values """
        return make_password(password)


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "password"]

    @staticmethod
    def validate_password(password) -> str:
        """ A function to save the password for storing the values """
        return make_password(password)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)
