from django.urls import path
from . import views

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('signup/', views.CreateUserViewSet.as_view()),
    path('login/', TokenObtainPairView.as_view(),
         name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(),
         name='token_refresh'),
    path('logout/', views.LogoutView.as_view(),
         name='logout'),
    path('logout-from-all/', views.LogoutAllView.as_view(),
         name='logout'),
]
