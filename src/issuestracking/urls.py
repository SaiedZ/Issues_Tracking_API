from django.urls import include, path
from . import views
from rest_framework_nested import routers

router = routers.DefaultRouter()

router.register(r'projects',
                views.ProjectViewSet,
                basename='projects')

contributors_router = routers.NestedDefaultRouter(router,
                                                  r'projects',
                                                  lookup='project')

contributors_router.register(r'users',
                             views.ContributorViewSet,
                             basename='project-contributors')

urlpatterns = [
    path(r'', include(router.urls)),
    path(r'', include(contributors_router.urls)),
]
