import logging
from rest_framework import status, viewsets, serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q

from .serializers import (
    # User serializers
    UserRegistrationSerializer,
    LoginSerializer,
    UserProfileSerializer,
    UserSerializer,

    # Server serializers
    ServerSerializer,
    ServerCreateSerializer,

    # Channel serializers
    ChannelSerializer,

    # Message serializers
    MessageSerializer,
    MessageCreateSerializer,
    MessageReactionSerializer,

    # Friend serializers
    FriendSerializer,
    FriendRequestSerializer,
    BlockedUserSerializer,

    # Notification serializers
    NotificationSerializer
)

from .models import UserProfile
from users.models import Users
from servers.models import Servers
from channels.models import Channels
from user_messages.models import UserMessages, MessageReaction
from friends.models import Friends, FriendRequest, BlockedUser
from notifications.models import Notifications

logger = logging.getLogger(__name__)

# Authentication Views
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            serializer = UserRegistrationSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()
                token, _ = Token.objects.get_or_create(user=user)
                return Response({
                    'token': token.key,
                    'user_id': user.user_id,
                    'username': user.username,
                    'email': user.email
                }, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # Log the error for debugging
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Registration error: {str(e)}")
            # Return a more informative error response
            return Response(
                {'error': f"Registration failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            serializer = LoginSerializer(data=request.data)
            if serializer.is_valid():
                email = serializer.validated_data['email']
                password = serializer.validated_data['password']

                try:
                    user = Users.objects.get(email=email)
                    # Use Django's built-in check_password method
                    if user.check_password(password):
                        token, _ = Token.objects.get_or_create(user=user)
                        return Response({
                            'token': token.key,
                            'user_id': user.user_id,
                            'username': user.username,
                            'email': user.email
                        })
                    else:
                        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
                except Users.DoesNotExist:
                    return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # Log the error for debugging
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Login error: {str(e)}")
            # Return a more informative error response
            return Response(
                {'error': f"Login failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.user.auth_token.delete()
        return Response({'message': 'Successfully logged out'}, status=status.HTTP_200_OK)

# User Profile Views
class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            profile = UserProfile.objects.get(user=request.user)
            serializer = UserProfileSerializer(profile)
            return Response(serializer.data)
        except UserProfile.DoesNotExist:
            return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request):
        try:
            profile = UserProfile.objects.get(user=request.user)
            serializer = UserProfileSerializer(profile, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except UserProfile.DoesNotExist:
            return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)

# Server Views
class ServerListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get servers where the user is the owner
        servers = Servers.objects.filter(owner_id=request.user)
        serializer = ServerSerializer(servers, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ServerCreateSerializer(data=request.data)
        if serializer.is_valid():
            # Set the owner to the current user
            serializer.validated_data['owner_id'] = request.user
            server = serializer.save()
            # Return the created server with its details
            return_serializer = ServerSerializer(server)
            return Response(return_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ServerDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        try:
            return Servers.objects.get(pk=pk, owner_id=user)
        except Servers.DoesNotExist:
            return None

    def get(self, request, pk):
        server = self.get_object(pk, request.user)
        if not server:
            return Response({'error': 'Server not found or you do not have permission'},
                            status=status.HTTP_404_NOT_FOUND)

        serializer = ServerSerializer(server)
        return Response(serializer.data)

    def put(self, request, pk):
        server = self.get_object(pk, request.user)
        if not server:
            return Response({'error': 'Server not found or you do not have permission'},
                            status=status.HTTP_404_NOT_FOUND)

        serializer = ServerSerializer(server, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        server = self.get_object(pk, request.user)
        if not server:
            return Response({'error': 'Server not found or you do not have permission'},
                            status=status.HTTP_404_NOT_FOUND)

        server.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# Channel Views
class ChannelViewSet(viewsets.ModelViewSet):
    serializer_class = ChannelSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        server_id = self.kwargs.get('server_id')
        if server_id:
            server = get_object_or_404(Servers, server_id=server_id)

            # Check if user is a member of the server
            if server.owner_id != self.request.user:
                return Channels.objects.none()

            return Channels.objects.filter(discord_server_id=server)
        return Channels.objects.none()

    def perform_create(self, serializer):
        server_id = self.kwargs.get('server_id')
        server = get_object_or_404(Servers, server_id=server_id)

        # Check if user is the owner
        if server.owner_id != self.request.user:
            raise PermissionError("You don't have permission to create channels")

        serializer.save(discord_server_id=server)

# Message Views
class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        channel_id = self.kwargs.get('channel_id')
        if channel_id:
            channel = get_object_or_404(Channels, channel_id=channel_id)

            # Check if user has access to this channel
            server = channel.discord_server_id
            if server.owner_id != self.request.user:
                return UserMessages.objects.none()

            return UserMessages.objects.filter(message_channel_id=channel).order_by('time_stamp')
        return UserMessages.objects.none()

    def perform_create(self, serializer):
        channel_id = self.kwargs.get('channel_id')
        channel = get_object_or_404(Channels, channel_id=channel_id)

        # Check if user has access to this channel
        server = channel.discord_server_id
        if server.owner_id != self.request.user:
            raise PermissionError("You don't have access to this channel")

        serializer.save(
            message_channel_id=channel,
            user_channel_id=self.request.user
        )

    @action(detail=True, methods=['post'])
    def react(self, request, pk=None, channel_id=None):
        message = self.get_object()
        emoji = request.data.get('emoji')

        if not emoji:
            return Response({'error': 'Emoji is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if reaction already exists
        reaction, created = MessageReaction.objects.get_or_create(
            message=message,
            user=request.user,
            emoji=emoji
        )

        if not created:
            # If reaction already exists, remove it (toggle behavior)
            reaction.delete()
            return Response({'message': 'Reaction removed'})

        serializer = MessageReactionSerializer(reaction)
        return Response(serializer.data)

# Friend Views
class FriendRequestViewSet(viewsets.ModelViewSet):
    serializer_class = FriendRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return FriendRequest.objects.filter(
            Q(sender=self.request.user) | Q(receiver=self.request.user)
        )

    def perform_create(self, serializer):
        receiver_id = self.request.data.get('receiver')
        receiver = get_object_or_404(Users, user_id=receiver_id)

        # Check if user is trying to add themselves
        if receiver == self.request.user:
            raise serializers.ValidationError("You cannot send a friend request to yourself")

        # Check if they are already friends
        if Friends.objects.filter(
            (Q(users_id=self.request.user) & Q(user_friend_id=receiver)) |
            (Q(users_id=receiver) & Q(user_friend_id=self.request.user))
        ).exists():
            raise serializers.ValidationError("You are already friends with this user")

        # Check if there's already a pending request
        if FriendRequest.objects.filter(
            (Q(sender=self.request.user) & Q(receiver=receiver)) |
            (Q(sender=receiver) & Q(receiver=self.request.user)),
            status='pending'
        ).exists():
            raise serializers.ValidationError("A friend request already exists between you and this user")

        # Check if user is blocked
        if BlockedUser.objects.filter(
            (Q(user=self.request.user) & Q(blocked_user=receiver)) |
            (Q(user=receiver) & Q(blocked_user=self.request.user))
        ).exists():
            raise serializers.ValidationError("You cannot send a friend request to a blocked user")

        serializer.save(sender=self.request.user, receiver=receiver, status='pending')

        # Create notification for the receiver
        Notifications.objects.create(
            user_id=receiver,
            notification_type='friend_request',
            friend_request=serializer.instance,
            title='New Friend Request',
            content=f'{self.request.user.username} sent you a friend request'
        )

    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        friend_request = self.get_object()

        # Check if user is the receiver
        if friend_request.receiver != request.user:
            return Response({'error': 'You cannot accept this request'}, status=status.HTTP_403_FORBIDDEN)

        # Check if request is pending
        if friend_request.status != 'pending':
            return Response({'error': 'This request has already been processed'}, status=status.HTTP_400_BAD_REQUEST)

        # Update request status
        friend_request.status = 'accepted'
        friend_request.save()

        # Create friend relationship
        Friends.objects.create(users_id=friend_request.receiver, user_friend_id=friend_request.sender)
        Friends.objects.create(users_id=friend_request.sender, user_friend_id=friend_request.receiver)

        # Create notification for the sender
        Notifications.objects.create(
            user_id=friend_request.sender,
            notification_type='friend_request',
            friend_request=friend_request,
            title='Friend Request Accepted',
            content=f'{request.user.username} accepted your friend request'
        )

        return Response({'message': 'Friend request accepted'})

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        friend_request = self.get_object()

        # Check if user is the receiver
        if friend_request.receiver != request.user:
            return Response({'error': 'You cannot reject this request'}, status=status.HTTP_403_FORBIDDEN)

        # Check if request is pending
        if friend_request.status != 'pending':
            return Response({'error': 'This request has already been processed'}, status=status.HTTP_400_BAD_REQUEST)

        # Update request status
        friend_request.status = 'rejected'
        friend_request.save()

        return Response({'message': 'Friend request rejected'})

class FriendListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        friends = Friends.objects.filter(users_id=request.user, status=True)
        serializer = FriendSerializer(friends, many=True)
        return Response(serializer.data)

class BlockedUserViewSet(viewsets.ModelViewSet):
    serializer_class = BlockedUserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return BlockedUser.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        blocked_user_id = self.request.data.get('blocked_user')
        blocked_user = get_object_or_404(Users, user_id=blocked_user_id)

        # Check if user is trying to block themselves
        if blocked_user == self.request.user:
            raise serializers.ValidationError("You cannot block yourself")

        # Remove any friend relationships
        Friends.objects.filter(
            (Q(users_id=self.request.user) & Q(user_friend_id=blocked_user)) |
            (Q(users_id=blocked_user) & Q(user_friend_id=self.request.user))
        ).delete()

        # Cancel any pending friend requests
        FriendRequest.objects.filter(
            (Q(sender=self.request.user) & Q(receiver=blocked_user)) |
            (Q(sender=blocked_user) & Q(receiver=self.request.user)),
            status='pending'
        ).update(status='rejected')

        serializer.save(user=self.request.user, blocked_user=blocked_user)

# Notification Views
class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notifications.objects.filter(user_id=self.request.user)

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'message': 'Notification marked as read'})

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        Notifications.objects.filter(user_id=request.user, is_read=False).update(is_read=True)
        return Response({'message': 'All notifications marked as read'})
