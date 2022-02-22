from django.http import Http404
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .permissions import IsOwnerOrContributorForReadOnly
from . import serializers, models, utils


class MultipleSerializerMixin:
    """
    Manages the choice of serialization depending on the method
    """

    def get_serializer_class(self):
        if self.action in self.serializers.keys():
            return self.serializers[self.action]
        return self.serializers['default']


class ProjectViewSet(MultipleSerializerMixin, viewsets.ModelViewSet):
    """
    Project View based on ModelViewSet
    """

    serializers = {
        'default': serializers.ProjectListSerializer,
        'retrieve': serializers.ProjectDetailSerializer,
    }

    permission_classes = [
        IsAuthenticated,
        IsOwnerOrContributorForReadOnly
    ]

    def get_queryset(self):
        """
        Get the list of items for this view.
        """
        user_projects_id = utils.get_user_projects_id(self.request.user)
        return models.Project.objects.filter(id__in=user_projects_id)


class ContributorViewSet(MultipleSerializerMixin, viewsets.ModelViewSet):
    """
    Contributor view based on ModelViewSet
    """

    serializers = {
        'default': serializers.ContributorSerializer,
        'create': serializers.ContributorCreateSerializer,
    }

    http_method_names = ['get', 'post', 'delete', 'head', 'options']

    def get_queryset(self):
        """
        Get the list of items for this view.
        """
        project_pk = self.kwargs["project_pk"]
        if not project_pk.isnumeric():
            raise Http404("No matches the given query")
        """if not models.Contributor.objects.filter(project_pk=project_pk).exists():
            print(not models.Contributor.objects.filter(project_pk=project_pk).exists())
            raise Http404("No matches the given query")"""
        return models.Contributor.objects.filter(project_id=project_pk)

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        context = super().get_serializer_context()
        context["project_pk"] = self.kwargs["project_pk"]
        return context

    """def list(self, request, project_pk=None, *args, **kwargs):
        if not project_pk.isnumeric():
            return Response(status=status.HTTP_404_NOT_FOUND)
        project = get_object_or_404(models.Project, id=project_pk)
        self.check_object_permissions(request, project)
        if not models.Project.objects.filter(id=project_pk).exists():
            return Response(status=status.HTTP_404_NOT_FOUND)
        queryset = models.Contributor.objects.filter(project=project_pk)
        serializer = self.get_serializer_class()(queryset, many=True)
        return Response(serializer.data)"""
