from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from django.http import Http404
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .permissions import (IsOwnerOrContributorForReadOnly,
                          IsProjectManagerOrReadOnlyContributorObject,
                          IsIssueOwnerOrReadOnlyIssueObject,
                          IsIssueOwnerOrReadOnlyCommentObject)
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

    def get_queryset(self):
        """
        Get the list of items for this view.
        """
        return models.Contributor.objects.filter(
            project_id=self.kwargs["project_pk"])

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        context = super().get_serializer_context()
        context["project_pk"] = self.kwargs["project_pk"]
        return context


class IssueViewSet(utils.MultipleSerializerMixin, viewsets.ModelViewSet):
    """
    Issue view based on ModelViewSet
    """

    serializers = {
        'default': serializers.IssueSerializer,
    }

    permission_classes = [IsIssueOwnerOrReadOnlyIssueObject]

    def get_queryset(self):
        """
        Get the list of items for this view.
        """
        return models.Issue.objects.filter(
            project_id=self.kwargs["project_pk"])

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        context = super().get_serializer_context()
        '''self.validate_parent_lookup_kwargs()'''
        context["project_pk"] = self.kwargs["project_pk"]
        context["view_action"] = self.action
        context["request"] = self.request
        return context


class CommentViewSet(utils.MultipleSerializerMixin, viewsets.ModelViewSet):
    """
    Comment view based on ModelViewSet
    """

    serializers = {
        'default': serializers.CommentSerializer,
    }
    http_method_names = ['get', 'post', 'delete', 'put', 'option', 'head']
    permission_classes = [IsIssueOwnerOrReadOnlyCommentObject]

    def get_queryset(self):
        """
        Get the list of items for this view.

        Verrify also that the issue_pk is part of the project_pk,
        otherwise it will raise a 404
        """
        queryset = models.Comment.objects.select_related('issue').filter(
            issue_id=self.kwargs["issue_pk"])
        if (
            not queryset.exists()
            or str(queryset[0].issue.project_id) != self.kwargs["project_pk"]
        ):
            raise Http404("No matches the given query")
        return queryset

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        context = super().get_serializer_context()
        context["issue_pk"] = self.kwargs["issue_pk"]
        context["view_action"] = self.action
        context["request"] = self.request
        return context
