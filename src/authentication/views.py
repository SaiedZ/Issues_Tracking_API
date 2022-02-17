from authentication.serializers import CreateUserSerializer
from rest_framework import generics
from . import models


class CreateUserViewSet(generics.CreateAPIView):
    """
    Handels the creatinon of user
    """

    serializer_class = CreateUserSerializer
    queryset = models.User.objects.all()
