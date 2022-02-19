from django.http import Http404
from rest_framework import viewsets
from . import serializers, models
from django.shortcuts import get_list_or_404, get_object_or_404


class MultipleSerializerMixin:
    """
    Manages the choice of serialization depending on the method
    """

    detail_serializer_class, creation_serializer_class = None, None

    def get_serializer_class(self):
        if self.action == 'retrieve'\
         and self.detail_serializer_class is not None:
            return self.detail_serializer_class
        elif self.action in ['create', 'update']\
         and self.creation_serializer_class is not None:
            return self.creation_serializer_class
        return super().get_serializer_class()


class ProjectViewSet(MultipleSerializerMixin, viewsets.ModelViewSet):
    """
    Project View based on ModelViewSet
    """

    serializer_class = serializers.ProjectListSerializer
    detail_serializer_class = serializers.ProjectDetailSerializer

    def get_queryset(self):
        return models.Project.objects.all()


class ContributorViewSet(MultipleSerializerMixin, viewsets.ModelViewSet):
    """
    Contributor view based on ModelViewSet
    """

    serializer_class = serializers.ContributorSerializer
    creation_serializer_class = serializers.ContributorCreateSerializer

    def get_queryset(self):
        """
        Get the list of items for this view.
        """
        project_id = self.kwargs["project_id"]
        if not project_id.isdigit():
            raise Http404("No matches the given query")
        else:
            queryset = models.Contributor.objects.filter(project_id=project_id)
        return queryset

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        context = super().get_serializer_context()
        context["project_id"] = self.kwargs["project_id"]
        return context
