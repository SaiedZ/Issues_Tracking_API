from rest_framework import permissions
from . import models, views

SAFE_ACTIONS = ['list', 'retrieve']
RESTRICTED_SAFE_ACTIONS = ['list']


class CheckIsProjectMemberOrContrCreaMixin:

    def get_model_view(self, view):
        if type(view) == views.IssueViewSet:
            model_view = models.Issue
        if type(view) == views.ContributorViewSet:
            model_view = models.Contributor
        if type(view) == views.CommentViewSet:
            model_view = models.Comment
        return model_view

    def has_permission(self, request, view):
        """
        Only project staff and project manager have
        access to list and create action

        Exception: For Contributor objects, CREA permission is
        requiered for creating (adding) contributor
        """
        project_pk = view.kwargs.get('project_pk')
        if not project_pk.isnumeric():
            return False
        user_contributor = models.Contributor.objects.filter(
            project_id=project_pk, user_id=request.user.id
        )
        user_contributor_exist = user_contributor.exists()

        if (
            user_contributor_exist
            and view.action == 'create'
            and self.get_model_view(view) == models.Contributor
        ):
            return user_contributor[0].permission == "CREA"
        return user_contributor_exist


class IsOwnerOrContributorForReadOnly(permissions.BasePermission):
    """
    Custom permission to allow only the Project Manager to edit or delete.
    Contributors have ReadOnly permission
    """

    def has_object_permission(self, request, view, obj):
        contributor_project = models.Contributor.objects.filter(
            project_id=obj.id, user_id=request.user.id)
        if view.action in SAFE_ACTIONS and contributor_project.exists():
            return True
        return contributor_project[0].permission == 'CREA'


class IsProjectManagerOrReadOnlyContributorObject(
     CheckIsProjectMemberOrContrCreaMixin, permissions.BasePermission):
    """
    Manages permissions for Contributor objects.
    """

    def has_object_permission(self, request, view, obj):
        """
        Only project manager is allowed to add and delete contributor
        It's frobidden to delete the Project Manager's contributor object
        """
        if obj.permission == "CREA":
            return False
        user_contrib = models.Contributor.objects.filter(
            project_id=obj.project_id, user_id=request.user.id
        )
        if view.action in RESTRICTED_SAFE_ACTIONS and user_contrib.exists():
            return True
        return user_contrib[0].permission == "CREA"


class IsAuthorOrReadOnly(
     CheckIsProjectMemberOrContrCreaMixin, permissions.BasePermission):

    """
    Manages permissions for Comment objects.
    """

    def has_object_permission(self, request, view, obj):
        """
        Only author is allowed to update and delete a comment
        """
        project_pk = view.kwargs.get('project_pk')
        user_contrib = models.Contributor.objects.filter(
            project_id=project_pk, user_id=request.user.id
        )
        if (
            view.action in SAFE_ACTIONS
            and user_contrib.exists()
        ):
            return True
        return user_contrib[0].user_id == obj.author_user_id
