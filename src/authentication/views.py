from authentication.serializers import CreateUserSerializer
from rest_framework import generics
from rest_framework import permissions
from . import models


class CreateUserViewSet(generics.CreateAPIView):
    """
    Handels the creatinon of new users

    This view is only accessible for unauthenticated users
    """

    serializer_class = CreateUserSerializer
    queryset = models.User.objects.all()
    permission_classes = [~permissions.IsAuthenticated]
