from rest_framework.generics import get_object_or_404
from rest_framework import serializers
from django.contrib.auth import get_user_model

from issuestracking import utils

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
                                                        role='PM',
                                                        permission='CREA')
        contributor.save()
        return project


class ProjectDetailSerializer(serializers.ModelSerializer):
    """
    A serializer for project objects. Used for detail display
    """
    authors = serializers.SerializerMethodField()
    members = serializers.SerializerMethodField()

    class Meta:
        model = models.Project
        fields = ['id', 'title', 'description', 'type', 'authors', 'members']

    def get_authors(self, instance):
        queryset = models.Contributor.objects.filter(project=instance,
                                                     permission='CREA')
        serializer = ContributorSerializer(queryset, many=True)
        return serializer.data

    def get_members(self, instance):
        queryset = models.Contributor.objects.filter(project=instance,
                                                     permission='CONT')
        serializer = ContributorSerializer(queryset, many=True)
        return serializer.data


class ContributorSerializer(serializers.ModelSerializer):
    """
    A serializer for contributo objects.
    """
    role = serializers.CharField(source='get_role_display')
    permission = serializers.CharField(source='get_permission_display')

    class Meta:
        model = models.Contributor
        fields = ['id', 'user', 'project', 'role', 'permission']


class ContributorCreateSerializer(serializers.ModelSerializer):
    """
    A serializer for contributo objects.
    """

    def __init__(self, *args, **kwargs):
        """
        Create the instance and set default value for `project` and
        the queryset for `user`
        """
        super().__init__(*args, **kwargs)
        self.fields['user'] = serializers.PrimaryKeyRelatedField(
            queryset=self.get_user_queryset())
        self.fields['project'] = serializers.HiddenField(
            default=self.get_project_queryset())

    class Meta:
        model = models.Contributor
        fields = ['id', 'user', 'project']

    def get_project_queryset(self):
        project_pk = self.context.get("project_pk")
        return get_object_or_404(models.Project, pk=project_pk)

    def get_user_queryset(self):
        project_pk = self.context.get("project_pk")
        users_id_to_exclude = utils.get_project_users_id(project_pk)
        return User.objects.exclude(id__in=users_id_to_exclude)
