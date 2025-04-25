from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    # Authentication views
    RegisterView,
    LoginView,
    LogoutView,

    # User views
    UserProfileView,

    # Server views
    ServerListCreateView,
    ServerDetailView,

    # Channel views
    ChannelViewSet,

    # Message views
    MessageViewSet,

    # Friend views
    FriendRequestViewSet,
    FriendListView,
    BlockedUserViewSet,

    # Notification views
    NotificationViewSet
)

# Create routers for ViewSets
router = DefaultRouter()
router.register(r'channels/(?P<server_id>\d+)', ChannelViewSet, basename='channel')
router.register(r'messages/(?P<channel_id>\d+)', MessageViewSet, basename='message')
router.register(r'friend-requests', FriendRequestViewSet, basename='friend-request')
router.register(r'blocked-users', BlockedUserViewSet, basename='blocked-user')
router.register(r'notifications', NotificationViewSet, basename='notification')

urlpatterns = [
    # Include router URLs
    path('', include(router.urls)),

    # Authentication endpoints
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),

    # User endpoints
    path('profile/', UserProfileView.as_view(), name='user-profile'),

    # Server endpoints
    path('servers/', ServerListCreateView.as_view(), name='server-list-create'),
    path('servers/<int:pk>/', ServerDetailView.as_view(), name='server-detail'),

    # Friend endpoints
    path('friends/', FriendListView.as_view(), name='friend-list'),
]
