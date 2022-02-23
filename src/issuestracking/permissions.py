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
        return model_view

    def has_permission(self, request, view):
        """
        Only project staff and project manager have
        access to list and create action

        Exception: For Contributor objects, CREA permission is
        requiered for creating (adding) contributor
        """
        project_pk = view.kwargs.get('project_pk')
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

    '''def has_permission_queryset(self, request, view, user_field):
        project_pk = view.kwargs.get('project_pk')
        filter_kwargs = {
            f"{user_field}": request.user,
            }
        return self.get_model_view(view).objects.filter(
            project_id=project_pk, **filter_kwargs)

    def has_permission(self, request, view):
        """
        Only project staff and project manager have access to contributors
        """
        print('has_permission', view.action)
        user_field = 'assignee_user'
        print(self.has_permission_queryset(request, view, user_field))
        return self.has_permission_queryset(
            request, view, user_field).exists()'''


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


class IsIssueOwnerOrReadOnlyIssueObject(
     CheckIsProjectMemberOrContrCreaMixin, permissions.BasePermission):

    """
    Manages permissions for Issue objects.
    """

    def has_object_permission(self, request, view, obj):
        """
        Only author or assignee users are allowed to update and delete issue
        """
        authorized_users_id = [
            obj.assignee_user_id,
            obj.author_user_id,
        ]
        user_contrib = models.Contributor.objects.filter(
            project_id=obj.project_id, user_id=request.user.id
        )
        if (
            view.action in RESTRICTED_SAFE_ACTIONS
            and user_contrib.exists()
        ):
            return True
        return user_contrib[0].user_id in authorized_users_id
