from .models import User
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import PasswordField
'''from django.contrib.auth.hashers import make_password'''


class CreateUserSerializer(serializers.ModelSerializer):
    """ Serializer for User model """

    password = PasswordField()

    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'first_name', 'last_name']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate_password(self, password):
        if validate_password(password) is None:
            # return make_password(password)
            return password

    def create(self, validated_data):
        """ Create and return new user"""

        user = super().create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    """ Serializer for User model """

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']
