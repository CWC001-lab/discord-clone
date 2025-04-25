from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    # Authentication views
    RegisterView,
    LoginView,
    LogoutView,

    # User views
    UserProfileView,
    UserBrowseView,

    # Server views
    ServerListCreateView,
    ServerDetailView,
    PublicServerListView,
    ServerJoinView,
    ServerMembersView,
    ServerMemberDetailView,
    ServerRolesView,
    ServerRoleDetailView,
    ServerInvitesView,
    ServerInviteDetailView,
    JoinServerByInviteView,

    # Channel views
    ChannelViewSet,
    DirectMessageChannelsView,
    DirectMessageUserView,

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
    path('servers/public/', PublicServerListView.as_view(), name='public-server-list'),
    path('servers/join/', JoinServerByInviteView.as_view(), name='join-server-by-invite'),
    path('servers/<int:pk>/', ServerDetailView.as_view(), name='server-detail'),
    path('servers/<int:pk>/join/', ServerJoinView.as_view(), name='server-join'),

    # Server Members
    path('servers/<int:server_id>/members/', ServerMembersView.as_view(), name='server-members'),
    path('servers/<int:server_id>/members/<int:member_id>/', ServerMemberDetailView.as_view(), name='server-member-detail'),

    # Server Roles
    path('servers/<int:server_id>/roles/', ServerRolesView.as_view(), name='server-roles'),
    path('servers/<int:server_id>/roles/<int:role_id>/', ServerRoleDetailView.as_view(), name='server-role-detail'),

    # Server Invites
    path('servers/<int:server_id>/invites/', ServerInvitesView.as_view(), name='server-invites'),
    path('invites/<int:invite_id>/', ServerInviteDetailView.as_view(), name='server-invite-detail'),

    # Direct Message endpoints
    path('channels/@me/', DirectMessageChannelsView.as_view(), name='direct-messages'),
    path('channels/@me/<int:user_id>/', DirectMessageUserView.as_view(), name='direct-message-user'),

    # Friend endpoints
    path('friends/', FriendListView.as_view(), name='friend-list'),
    path('users/browse/', UserBrowseView.as_view(), name='user-browse'),
]
