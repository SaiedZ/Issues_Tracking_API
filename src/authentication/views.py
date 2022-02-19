from authentication.serializers import CreateUserSerializer
from rest_framework import generics
from . import models, permissions


class CreateUserViewSet(generics.CreateAPIView):
    """
    Handels the creatinon of new users

    This view is only accessible for unauthenticated users
    """

    serializer_class = CreateUserSerializer
    queryset = models.User.objects.all()
    permission_classes = [permissions.IsNotAuthenticated]
