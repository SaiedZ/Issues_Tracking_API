from rest_framework.generics import get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework import serializers

import authentication
from . import models

User = get_user_model()


class ProjectListSerializer(serializers.ModelSerializer):
    """
    A serializer for project objects, list display.
    """
    class Meta:
        model = models.Project
        fields = ['id', 'title', 'description', 'type']

    def create(self, validated_data):
        """
        Create and return a new `Project` instance, given the validated data.

        Create a contributor with the CREATOR role and the current project.
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
    A serializer for contributor objects.
    """
    role = serializers.CharField(source='get_role_display')
    permission = serializers.CharField(source='get_permission_display')
    user = authentication.serializers.UserSerializer()
    project = serializers.SlugRelatedField(read_only=True, slug_field='title')

    class Meta:
        model = models.Contributor
        fields = ['id', 'user', 'project', 'role', 'permission']


class ContributorCreateSerializer(serializers.ModelSerializer):
    """
    A serializer for creating contributor objects.
    """

    def __init__(self, *args, **kwargs):
        """
        Create the instance and set default value for `project` and
        the queryset for `user`
        """
        super().__init__(*args, **kwargs)
        self.fields['user'] = serializers.SlugRelatedField(
            queryset=self.get_user_queryset(), slug_field='username')
        self.fields['project'] = serializers.HiddenField(
            default=self.get_project_queryset())

    class Meta:
        model = models.Contributor
        fields = ['id', 'user', 'role', 'permission']

    def get_project_queryset(self):
        project_pk = self.context.get("project_pk")
        return get_object_or_404(models.Project, pk=project_pk)

    def get_user_queryset(self):
        project_pk = self.context.get("project_pk")
        return User.objects.exclude(users__project_id=project_pk)


class IssueSerializer(serializers.ModelSerializer):
    """
    A serializer for issue objects.
    """
    project = serializers.SlugRelatedField(read_only=True, slug_field='title')

    def __init__(self, *args, **kwargs):
        """
        Initialize and if the view action is `create`:
            - the assignee will be by default the request user
            - the project will be set using the project_id from the url
            - the author is request.user
        """
        super().__init__(*args, **kwargs)
        self.fields['assignee_user'] = serializers.SlugRelatedField(
            queryset=self.get_user_queryset(),
            initial=self.context.get('request').user.username,
            slug_field='username'
            )
        if self.context['view_action'] == 'create':
            self.fields['project'] = serializers.HiddenField(
                default=self.get_project_queryset())
            self.fields['author_user'] = serializers.HiddenField(
                default=self.context.get('request').user)

    class Meta:
        model = models.Issue
        fields = '__all__'

    def get_project_queryset(self):
        project_pk = self.context.get("project_pk")
        return get_object_or_404(models.Project, pk=project_pk)

    def get_user_queryset(self):
        project_pk = self.context.get("project_pk")
        return User.objects.filter(users__project_id=project_pk)

    def to_representation(self, instance):
        """
        Object instance -> Dict of primitive datatypes.
        modifies the format of created_time
        """
        ret = super().to_representation(instance)
        ret['created_time'] = instance.created_time.strftime(
            "%H:%M:%S %d-%m-%Y")
        return ret


class CommentSerializer(serializers.ModelSerializer):
    """
    A serializer for comment objects.
    """
    issue = serializers.SlugRelatedField(read_only=True, slug_field='title')

    class Meta:
        model = models.Comment
        fields = '__all__'
        read_only_fields = ['issue', 'author_user']

    def create(self, validated_data):
        """ Create and return new comment"""

        comment = super().create(validated_data)
        comment.issue = self.get_issue_queryset()
        comment.author_user = self.context.get('request').user
        comment.save()
        return comment

    def get_issue_queryset(self):
        issue_pk = self.context.get("issue_pk")
        return get_object_or_404(models.Issue, pk=issue_pk)

    def to_representation(self, instance):
        """
        Object instance -> Dict of primitive datatypes.
        modifies the format of created_time
        """
        ret = super().to_representation(instance)
        ret['created_time'] = instance.created_time.strftime(
            "%H:%M:%S %d-%m-%Y")
        return ret
