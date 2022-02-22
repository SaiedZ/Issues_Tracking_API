from .models import Contributor


class MultipleSerializerMixin:
    """
    Manages the choice of serialization depending on the action
    """

    def get_serializer_class(self):
        if self.action in self.serializers.keys():
            return self.serializers[self.action]
        return self.serializers['default']


def get_project_users_id(project_id):
    return [
        contributor.user.id for contributor in Contributor.objects.filter(
            project_id=project_id)
        ]


def get_user_projects_id(user):
    return [
        contributor.project.id for
        contributor in Contributor.objects.filter(user=user)
        ]
