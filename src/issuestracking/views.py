from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from django.http import Http404
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .permissions import (IsOwnerOrContributorForReadOnly,
                          IsProjectManagerOrReadOnlyContributorObject,
                          IsIssueOwnerOrReadOnlyIssueObject)
from . import serializers, models, utils


class ProjectViewSet(utils.MultipleSerializerMixin, viewsets.ModelViewSet):
    """
    Project View based on ModelViewSet
    """

    serializers = {
        'default': serializers.ProjectListSerializer,
        'retrieve': serializers.ProjectDetailSerializer,
    }

    permission_classes = [IsAuthenticated & IsOwnerOrContributorForReadOnly]

    def get_queryset(self):
        """
        Get the list of items for this view.
        """
        return models.Project.objects.filter(
            projects__user_id=self.request.user.id).distinct()


class ContributorViewSet(utils.MultipleSerializerMixin, viewsets.ModelViewSet):
    """
    Contributor view based on ModelViewSet
    """

    serializers = {
        'default': serializers.ContributorSerializer,
        'create': serializers.ContributorCreateSerializer,
    }
    http_method_names = ['get', 'post', 'delete', 'option', 'head']
    permission_classes = [IsProjectManagerOrReadOnlyContributorObject]

    def validate_project_id(self):
        """
        Ensure that the project_id is valid (is integer)
        """
        project_pk = self.kwargs["project_pk"]
        if not project_pk.isnumeric():
            raise Http404("No matches the given query")
        return project_pk

    def get_queryset(self):
        """
        Get the list of items for this view.
        """
        project_pk = self.validate_project_id()
        return models.Contributor.objects.filter(project_id=project_pk)

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        context = super().get_serializer_context()
        context["project_pk"] = self.validate_project_id()
        return context


class IssueViewSet(utils.MultipleSerializerMixin, viewsets.ModelViewSet):
    """
    Issue view based on ModelViewSet
    """

    serializers = {
        'default': serializers.IssueSerializer,
    }

    permission_classes = [IsIssueOwnerOrReadOnlyIssueObject]

    def validate_project_id(self):
        """
        Ensure that the project_id is valid (is integer)
        """
        project_pk = self.kwargs["project_pk"]
        if not project_pk.isnumeric():
            raise Http404("No matches the given query")
        return project_pk

    def get_queryset(self):
        """
        Get the list of items for this view.
        """
        project_pk = self.validate_project_id()
        return models.Issue.objects.filter(project_id=project_pk)

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        context = super().get_serializer_context()
        context["project_pk"] = self.validate_project_id()
        context["view_action"] = self.action
        context["request"] = self.request
        return context
