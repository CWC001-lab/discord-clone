from django.urls import path
from .views import (
    RegisterView,
    LoginView,
    LogoutView,
    UserProfileView,
    ServerListCreateView,
    ServerDetailView
)

urlpatterns = [
    # Authentication endpoints
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),

    # User profile endpoints
    path('profile/', UserProfileView.as_view(), name='user-profile'),

    # Server endpoints
    path('servers/', ServerListCreateView.as_view(), name='server-list-create'),
    path('servers/<int:pk>/', ServerDetailView.as_view(), name='server-detail'),
]
