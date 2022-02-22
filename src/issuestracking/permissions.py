from rest_framework import permissions
from . import models, utils

SAFE_ACTIONS = ['list', 'retrieve']
CONTRIBUTOR_SAFE_ACTIONS = ['list']


class IsOwnerOrContributorForReadOnly(permissions.BasePermission):
    """
    Custom permission to allow only the Project Manager to edit or delete.

    Contributors have ReadOnly permission
    """

    def has_object_permission(self, request, view, obj):
        # read permissions are only allowed to the contributors of the project.
        contributor_project = models.Contributor.objects.filter(
            project_id=obj.id, user_id=request.user.id)
        if view.action in SAFE_ACTIONS and contributor_project.exists():
            return True
        # Write permissions are only allowed to the author of the project.
        return contributor_project[0].permission == 'CREA'


class IsProjectManagerOrReadOnlyContributorObject(permissions.BasePermission):
    """
    Manages permissions for Contributor objects.
    """

    def has_permission(self, request, view):
        """
        Only project staff and project manager have access to contributors
        """
        project_pk = view.kwargs.get('project_pk')
        return models.Contributor.objects.filter(
            project_id=project_pk, user_id=request.user.id).exists()

    def has_object_permission(self, request, view, obj):
        """
        Only project manager is allowed to add and delete contributor

        It's frobidden to delete the Project Manager's contributor object
        """
        if obj.permission == "CREA":
            return False
        user_contributor = models.Contributor.objects.filter(
            project_id=obj.project_id, user_id=request.user.id
        )
        if view.action in CONTRIBUTOR_SAFE_ACTIONS and user_contributor.exists():
            return True
        return user_contributor[0].permission == "CREA"


"""class CheckParentPermissionMixin:
    parent_queryset: object
    parent_lookup_field: int
    parent_lookup_url_kwarg: int

    def __init__(self, **kwargs):
        self.parent_obj = None
        super().__init__(**kwargs)

    def check_permissions(self, request):
        super().check_permissions(request)

        # check permissions for the parent object
        parent_lookup_url_kwarg = self.parent_lookup_url_kwarg or self.parent_lookup_field
        filter_kwargs = {
            self.parent_lookup_field: self.kwargs[parent_lookup_url_kwarg]
        }
        self.parent_obj = get_object_or_404(
            self.parent_queryset, **filter_kwargs)
        self.parent_obj._is_parent_obj = True
        super().check_object_permissions(request, self.parent_obj)"""
