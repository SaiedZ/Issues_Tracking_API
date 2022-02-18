from rest_framework import serializers
from django.contrib.auth import get_user_model

from . import models

User = get_user_model()


class ProjectListSerializer(serializers.ModelSerializer):
    """
    A serializer for project objects, list display
    """

    class Meta:
        model = models.Project
        fields = ['id', 'title', 'description', 'type']

    def create(self, validated_data):
        """
        Create and return a new `Project` instance, given the validated data.

        Create a contributor with the CREATOR role and the current project
        """
        project = super().create(validated_data)
        user = self.context['request'].user
        contributor = models.Contributor.objects.create(user=user,
                                                        project=project,
                                                        role='CREA')
        contributor.save()

        return project


class ProjectDetailSerializer(serializers.ModelSerializer):
    """
    A serializer for project objects.

    Used for detail display
    """

    author = serializers.SerializerMethodField()

    class Meta:
        model = models.Project
        fields = ['id', 'title', 'description', 'type', 'author']

    def get_author(self, instance):
        queryset = models.Contributor.objects.filter(project=instance,
                                                     role='CREATOR')
        serializer = ContributorSerializer(queryset, many=True)
        return serializer.data


class ContributorSerializer(serializers.ModelSerializer):
    """
    A serializer for contributo objects.
    """

    class Meta:
        model = models.Contributor
        fields = ['id', 'user', 'project', 'role']


class ContributorCreateSerializer(serializers.ModelSerializer):
    """
    A serializer for contributo objects.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user'] = serializers.PrimaryKeyRelatedField(
            queryset=self.get_user_queryset())
        self.fields['project'] = serializers.HiddenField(
            default=self.get_project_queryset()[0])

    class Meta:
        model = models.Contributor
        fields = ['id', 'user', 'project']

    def get_project_queryset(self):
        project_id = self.context.get("project_id")
        projects = models.Project.objects.filter(id=project_id)
        if projects:
            return projects
        return None

    def get_user_queryset(self):
        project_id = self.context.get("project_id")
        users_to_exclude = [
            contributor.user.id for contributor in models.Contributor.objects.filter(
                project_id=project_id)
            ]
        return User.objects.exclude(id__in=users_to_exclude)
