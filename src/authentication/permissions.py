from rest_framework import permissions


class IsNotAuthenticated(permissions.IsAuthenticated):
    """
    Allows access only to unauthenticated users.
    """

    def has_permission(self, request, view):
        return not super().has_permission(request, view)
