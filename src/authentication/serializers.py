from .models import User
from rest_framework import serializers


class CreateUserSerializer(serializers.ModelSerializer):
    """ Serializer for User model """

    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'first_name', 'last_name']
        extra_kwargs = {
            'password': {'write_only': True}
        }

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
