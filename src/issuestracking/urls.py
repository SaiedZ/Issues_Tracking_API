from django.urls import include, path
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter(trailing_slash=False)

router.register('projects',
                views.ProjectViewSet,
                basename='projects')

router.register('^projects/(?P<project_id>.+)/users',
                views.ContributorViewSet,
                basename='contributors')

urlpatterns = [
    path('', include(router.urls)),
]
