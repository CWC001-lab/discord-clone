import logging
import uuid
from datetime import timedelta
from rest_framework import status, viewsets, serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q
from django.db import utils as db_utils

from .serializers import (
    # User serializers
    UserRegistrationSerializer,
    LoginSerializer,
    UserProfileSerializer,
    UserSerializer,

    # Server serializers
    ServerSerializer,
    ServerCreateSerializer,
    ServerMemberSerializer,
    ServerRoleSerializer,
    ServerInviteSerializer,

    # Channel serializers
    ChannelSerializer,
    DirectMessageChannelSerializer,

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
from servers.models import Servers, ServerMember, ServerRole, ServerInvite
from channels.models import Channels, DirectMessageChannel
from user_messages.models import UserMessages, MessageReaction
from friends.models import Friends, FriendRequest, BlockedUser
from notifications.models import Notifications

logger = logging.getLogger(__name__)

# Authentication Views
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            # Log the request data for debugging
            logger.debug(f"Registration request data: {request.data}")

            serializer = UserRegistrationSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()
                token, _ = Token.objects.get_or_create(user=user)

                # Return a more complete response
                response_data = {
                    'token': token.key,
                    'user_id': user.user_id,
                    'username': user.username,
                    'email': user.email,
                    'display_name': user.display_name or user.username
                }

                logger.debug(f"Registration successful: {response_data}")
                return Response(response_data, status=status.HTTP_201_CREATED)

            # Log validation errors
            logger.error(f"Registration validation errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except db_utils.OperationalError as e:
            # Handle database connection errors
            error_msg = f"Database connection error: {str(e)}"
            logger.error(error_msg)
            return Response(
                {'error': "Registration failed due to database connection issues. Please try again later."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except Exception as e:
            # Log the error for debugging
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
            # Log the request data for debugging
            logger.debug(f"Login request data: {request.data}")

            serializer = LoginSerializer(data=request.data)
            if serializer.is_valid():
                email = serializer.validated_data['email']
                password = serializer.validated_data['password']

                try:
                    user = Users.objects.get(email=email)
                    # Use Django's built-in check_password method
                    if user.check_password(password):
                        token, _ = Token.objects.get_or_create(user=user)

                        # Return a more complete response
                        response_data = {
                            'token': token.key,
                            'user_id': user.user_id,
                            'username': user.username,
                            'email': user.email,
                            'display_name': user.display_name or user.username
                        }

                        logger.debug(f"Login successful: {response_data}")
                        return Response(response_data)
                    else:
                        logger.warning(f"Invalid credentials for user: {email}")
                        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
                except Users.DoesNotExist:
                    logger.warning(f"User not found: {email}")
                    return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

            # Log validation errors
            logger.error(f"Login validation errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except db_utils.OperationalError as e:
            # Handle database connection errors
            error_msg = f"Database connection error: {str(e)}"
            logger.error(error_msg)
            return Response(
                {'error': "Login failed due to database connection issues. Please try again later."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except Exception as e:
            # Log the error for debugging
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
        owned_servers = Servers.objects.filter(owner_id=request.user)

        # Get servers where the user is a member
        member_server_ids = ServerMember.objects.filter(user=request.user).values_list('server_id', flat=True)
        member_servers = Servers.objects.filter(server_id__in=member_server_ids).exclude(owner_id=request.user)

        # Combine the two querysets
        all_servers = list(owned_servers) + list(member_servers)

        serializer = ServerSerializer(all_servers, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ServerCreateSerializer(data=request.data)
        if serializer.is_valid():
            # Set the owner to the current user
            serializer.validated_data['owner_id'] = request.user
            server = serializer.save()

            # Add the owner as a member with 'owner' role
            ServerMember.objects.create(
                server=server,
                user=request.user,
                role='owner'
            )

            # Return the created server with its details
            return_serializer = ServerSerializer(server)
            return Response(return_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Public Server View
class PublicServerListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get all public servers
        # Filter for servers that are marked as public
        servers = Servers.objects.filter(is_public=True)

        # Exclude servers the user is already a member of
        user_server_ids = ServerMember.objects.filter(user=request.user).values_list('server_id', flat=True)
        servers = servers.exclude(server_id__in=user_server_ids)

        serializer = ServerSerializer(servers, many=True)
        return Response(serializer.data)

# Server Join View
class ServerJoinView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            server = Servers.objects.get(pk=pk)

            # Check if user is already a member
            if ServerMember.objects.filter(server=server, user=request.user).exists():
                return Response({"message": "You are already a member of this server"}, status=status.HTTP_200_OK)

            # Add user to server members
            member = ServerMember.objects.create(
                server=server,
                user=request.user,
                role='member'
            )

            # Serialize and return the member data
            serializer = ServerMemberSerializer(member)
            return Response({
                "message": "Server joined successfully",
                "member": serializer.data
            }, status=status.HTTP_201_CREATED)

        except Servers.DoesNotExist:
            return Response({"error": "Server not found"}, status=status.HTTP_404_NOT_FOUND)

class ServerDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Servers.objects.get(pk=pk)
        except Servers.DoesNotExist:
            return None

    def get(self, request, pk):
        server = self.get_object(pk)
        if not server:
            return Response({'error': 'Server not found'},
                            status=status.HTTP_404_NOT_FOUND)

        # Check if user is a member of the server
        if not ServerMember.objects.filter(server=server, user=request.user).exists():
            return Response({'error': 'You are not a member of this server'},
                            status=status.HTTP_403_FORBIDDEN)

        serializer = ServerSerializer(server)
        return Response(serializer.data)

    def put(self, request, pk):
        server = self.get_object(pk)
        if not server:
            return Response({'error': 'Server not found'},
                            status=status.HTTP_404_NOT_FOUND)

        # Check if user is the owner of the server
        if server.owner_id != request.user:
            return Response({'error': 'You do not have permission to update this server'},
                            status=status.HTTP_403_FORBIDDEN)

        serializer = ServerSerializer(server, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        server = self.get_object(pk)
        if not server:
            return Response({'error': 'Server not found'},
                            status=status.HTTP_404_NOT_FOUND)

        # Check if user is the owner of the server
        if server.owner_id != request.user:
            return Response({'error': 'You do not have permission to delete this server'},
                            status=status.HTTP_403_FORBIDDEN)

        server.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# Server Members View
class ServerMembersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, server_id):
        """
        Get all members of a server
        """
        try:
            # Check if server exists
            server = Servers.objects.get(pk=server_id)

            # Check if user is a member of the server
            if not ServerMember.objects.filter(server=server, user=request.user).exists():
                return Response({'error': 'You are not a member of this server'}, status=status.HTTP_403_FORBIDDEN)

            # Get all members
            members = ServerMember.objects.filter(server=server)
            serializer = ServerMemberSerializer(members, many=True)
            return Response(serializer.data)

        except Servers.DoesNotExist:
            return Response({'error': 'Server not found'}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, server_id):
        """
        Add a user to a server (invite)
        """
        try:
            # Check if server exists
            server = Servers.objects.get(pk=server_id)

            # Check if user is an admin or owner
            user_member = ServerMember.objects.get(server=server, user=request.user)
            if not user_member.has_permission('create_invites'):
                return Response({'error': 'You do not have permission to invite users'}, status=status.HTTP_403_FORBIDDEN)

            # Get the user to invite
            user_id = request.data.get('user_id')
            if not user_id:
                return Response({'error': 'User ID is required'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                user_to_invite = Users.objects.get(pk=user_id)
            except Users.DoesNotExist:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

            # Check if user is already a member
            if ServerMember.objects.filter(server=server, user=user_to_invite).exists():
                return Response({'error': 'User is already a member of this server'}, status=status.HTTP_400_BAD_REQUEST)

            # Add user to server
            member = ServerMember.objects.create(
                server=server,
                user=user_to_invite,
                role='member'
            )

            serializer = ServerMemberSerializer(member)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Servers.DoesNotExist:
            return Response({'error': 'Server not found'}, status=status.HTTP_404_NOT_FOUND)
        except ServerMember.DoesNotExist:
            return Response({'error': 'You are not a member of this server'}, status=status.HTTP_403_FORBIDDEN)

# Server Member Detail View
class ServerMemberDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, server_id, member_id):
        try:
            return ServerMember.objects.get(server_id=server_id, id=member_id)
        except ServerMember.DoesNotExist:
            return None

    def get(self, request, server_id, member_id):
        """
        Get details of a specific server member
        """
        # Check if server exists
        try:
            server = Servers.objects.get(pk=server_id)
        except Servers.DoesNotExist:
            return Response({'error': 'Server not found'}, status=status.HTTP_404_NOT_FOUND)

        # Check if user is a member of the server
        if not ServerMember.objects.filter(server=server, user=request.user).exists():
            return Response({'error': 'You are not a member of this server'}, status=status.HTTP_403_FORBIDDEN)

        # Get the member
        member = self.get_object(server_id, member_id)
        if not member:
            return Response({'error': 'Member not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ServerMemberSerializer(member)
        return Response(serializer.data)

    def put(self, request, server_id, member_id):
        """
        Update a server member (change role, nickname)
        """
        # Check if server exists
        try:
            server = Servers.objects.get(pk=server_id)
        except Servers.DoesNotExist:
            return Response({'error': 'Server not found'}, status=status.HTTP_404_NOT_FOUND)

        # Check if user has permission to manage roles
        try:
            user_member = ServerMember.objects.get(server=server, user=request.user)
            if not user_member.has_permission('manage_roles'):
                return Response({'error': 'You do not have permission to manage roles'}, status=status.HTTP_403_FORBIDDEN)
        except ServerMember.DoesNotExist:
            return Response({'error': 'You are not a member of this server'}, status=status.HTTP_403_FORBIDDEN)

        # Get the member to update
        member = self.get_object(server_id, member_id)
        if not member:
            return Response({'error': 'Member not found'}, status=status.HTTP_404_NOT_FOUND)

        # Cannot change the role of the server owner
        if member.role == 'owner' and request.data.get('role') and request.data.get('role') != 'owner':
            return Response({'error': 'Cannot change the role of the server owner'}, status=status.HTTP_400_BAD_REQUEST)

        # Update the member
        serializer = ServerMemberSerializer(member, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, server_id, member_id):
        """
        Remove a member from a server (kick)
        """
        # Check if server exists
        try:
            server = Servers.objects.get(pk=server_id)
        except Servers.DoesNotExist:
            return Response({'error': 'Server not found'}, status=status.HTTP_404_NOT_FOUND)

        # Check if user has permission to kick members
        try:
            user_member = ServerMember.objects.get(server=server, user=request.user)
            if not user_member.has_permission('kick_members'):
                return Response({'error': 'You do not have permission to kick members'}, status=status.HTTP_403_FORBIDDEN)
        except ServerMember.DoesNotExist:
            return Response({'error': 'You are not a member of this server'}, status=status.HTTP_403_FORBIDDEN)

        # Get the member to kick
        member = self.get_object(server_id, member_id)
        if not member:
            return Response({'error': 'Member not found'}, status=status.HTTP_404_NOT_FOUND)

        # Cannot kick the server owner
        if member.role == 'owner':
            return Response({'error': 'Cannot kick the server owner'}, status=status.HTTP_400_BAD_REQUEST)

        # Cannot kick yourself
        if member.user == request.user:
            return Response({'error': 'Cannot kick yourself'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the user has permission to kick this member
        # A member can only kick members with lower roles
        if user_member.role != 'owner' and member.role in ['admin', 'moderator'] and user_member.role != 'admin':
            return Response({'error': 'You do not have permission to kick this member'}, status=status.HTTP_403_FORBIDDEN)

        # Remove the member
        member.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# Server Roles View
class ServerRolesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, server_id):
        """
        Get all roles for a server
        """
        try:
            # Check if server exists
            server = Servers.objects.get(pk=server_id)

            # Check if user is a member of the server
            if not ServerMember.objects.filter(server=server, user=request.user).exists():
                return Response({'error': 'You are not a member of this server'}, status=status.HTTP_403_FORBIDDEN)

            # Get all roles
            roles = ServerRole.objects.filter(server=server)
            serializer = ServerRoleSerializer(roles, many=True)
            return Response(serializer.data)

        except Servers.DoesNotExist:
            return Response({'error': 'Server not found'}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, server_id):
        """
        Create a new role for a server
        """
        try:
            # Check if server exists
            server = Servers.objects.get(pk=server_id)

            # Check if user has permission to manage roles
            try:
                user_member = ServerMember.objects.get(server=server, user=request.user)
                if not user_member.has_permission('manage_roles'):
                    return Response({'error': 'You do not have permission to manage roles'}, status=status.HTTP_403_FORBIDDEN)
            except ServerMember.DoesNotExist:
                return Response({'error': 'You are not a member of this server'}, status=status.HTTP_403_FORBIDDEN)

            # Create the role
            serializer = ServerRoleSerializer(data=request.data)
            if serializer.is_valid():
                serializer.validated_data['server'] = server
                role = serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Servers.DoesNotExist:
            return Response({'error': 'Server not found'}, status=status.HTTP_404_NOT_FOUND)

# Server Role Detail View
class ServerRoleDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, server_id, role_id):
        try:
            return ServerRole.objects.get(server_id=server_id, id=role_id)
        except ServerRole.DoesNotExist:
            return None

    def get(self, request, server_id, role_id):
        """
        Get details of a specific server role
        """
        # Check if server exists
        try:
            server = Servers.objects.get(pk=server_id)
        except Servers.DoesNotExist:
            return Response({'error': 'Server not found'}, status=status.HTTP_404_NOT_FOUND)

        # Check if user is a member of the server
        if not ServerMember.objects.filter(server=server, user=request.user).exists():
            return Response({'error': 'You are not a member of this server'}, status=status.HTTP_403_FORBIDDEN)

        # Get the role
        role = self.get_object(server_id, role_id)
        if not role:
            return Response({'error': 'Role not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ServerRoleSerializer(role)
        return Response(serializer.data)

    def put(self, request, server_id, role_id):
        """
        Update a server role
        """
        # Check if server exists
        try:
            server = Servers.objects.get(pk=server_id)
        except Servers.DoesNotExist:
            return Response({'error': 'Server not found'}, status=status.HTTP_404_NOT_FOUND)

        # Check if user has permission to manage roles
        try:
            user_member = ServerMember.objects.get(server=server, user=request.user)
            if not user_member.has_permission('manage_roles'):
                return Response({'error': 'You do not have permission to manage roles'}, status=status.HTTP_403_FORBIDDEN)
        except ServerMember.DoesNotExist:
            return Response({'error': 'You are not a member of this server'}, status=status.HTTP_403_FORBIDDEN)

        # Get the role to update
        role = self.get_object(server_id, role_id)
        if not role:
            return Response({'error': 'Role not found'}, status=status.HTTP_404_NOT_FOUND)

        # Update the role
        serializer = ServerRoleSerializer(role, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, server_id, role_id):
        """
        Delete a server role
        """
        # Check if server exists
        try:
            server = Servers.objects.get(pk=server_id)
        except Servers.DoesNotExist:
            return Response({'error': 'Server not found'}, status=status.HTTP_404_NOT_FOUND)

        # Check if user has permission to manage roles
        try:
            user_member = ServerMember.objects.get(server=server, user=request.user)
            if not user_member.has_permission('manage_roles'):
                return Response({'error': 'You do not have permission to manage roles'}, status=status.HTTP_403_FORBIDDEN)
        except ServerMember.DoesNotExist:
            return Response({'error': 'You are not a member of this server'}, status=status.HTTP_403_FORBIDDEN)

        # Get the role to delete
        role = self.get_object(server_id, role_id)
        if not role:
            return Response({'error': 'Role not found'}, status=status.HTTP_404_NOT_FOUND)

        # Cannot delete the default role
        if role.is_default:
            return Response({'error': 'Cannot delete the default role'}, status=status.HTTP_400_BAD_REQUEST)

        # Delete the role
        role.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# Server Invites View
class ServerInvitesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, server_id):
        """
        Get all invites for a server
        """
        try:
            # Check if server exists
            server = Servers.objects.get(pk=server_id)

            # Check if user has permission to view invites
            try:
                user_member = ServerMember.objects.get(server=server, user=request.user)
                if not user_member.has_permission('create_invites'):
                    return Response({'error': 'You do not have permission to view invites'}, status=status.HTTP_403_FORBIDDEN)
            except ServerMember.DoesNotExist:
                return Response({'error': 'You are not a member of this server'}, status=status.HTTP_403_FORBIDDEN)

            # Get all invites
            invites = ServerInvite.objects.filter(server=server)
            serializer = ServerInviteSerializer(invites, many=True)
            return Response(serializer.data)

        except Servers.DoesNotExist:
            return Response({'error': 'Server not found'}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, server_id):
        """
        Create a new invite for a server
        """
        try:
            # Check if server exists
            server = Servers.objects.get(pk=server_id)

            # Check if user has permission to create invites
            try:
                user_member = ServerMember.objects.get(server=server, user=request.user)
                if not user_member.has_permission('create_invites'):
                    return Response({'error': 'You do not have permission to create invites'}, status=status.HTTP_403_FORBIDDEN)
            except ServerMember.DoesNotExist:
                return Response({'error': 'You are not a member of this server'}, status=status.HTTP_403_FORBIDDEN)

            # Create the invite
            max_uses = request.data.get('max_uses', 0)
            expires_in = request.data.get('expires_in', 0)  # in hours, 0 = never expires

            # Generate a unique invite code
            code = str(uuid.uuid4())[:8]

            # Calculate expiration date
            expires_at = None
            if expires_in > 0:
                expires_at = timezone.now() + timedelta(hours=expires_in)

            # Create the invite
            invite = ServerInvite.objects.create(
                server=server,
                code=code,
                created_by=request.user,
                max_uses=max_uses,
                expires_at=expires_at
            )

            serializer = ServerInviteSerializer(invite)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Servers.DoesNotExist:
            return Response({'error': 'Server not found'}, status=status.HTTP_404_NOT_FOUND)

# Server Invite Detail View
class ServerInviteDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, invite_id):
        try:
            return ServerInvite.objects.get(id=invite_id)
        except ServerInvite.DoesNotExist:
            return None

    def get(self, request, invite_id):
        """
        Get details of a specific server invite
        """
        # Get the invite
        invite = self.get_object(invite_id)
        if not invite:
            return Response({'error': 'Invite not found'}, status=status.HTTP_404_NOT_FOUND)

        # Check if user has permission to view this invite
        try:
            user_member = ServerMember.objects.get(server=invite.server, user=request.user)
            if not user_member.has_permission('create_invites'):
                return Response({'error': 'You do not have permission to view this invite'}, status=status.HTTP_403_FORBIDDEN)
        except ServerMember.DoesNotExist:
            return Response({'error': 'You are not a member of this server'}, status=status.HTTP_403_FORBIDDEN)

        serializer = ServerInviteSerializer(invite)
        return Response(serializer.data)

    def delete(self, request, invite_id):
        """
        Delete a server invite
        """
        # Get the invite
        invite = self.get_object(invite_id)
        if not invite:
            return Response({'error': 'Invite not found'}, status=status.HTTP_404_NOT_FOUND)

        # Check if user has permission to delete this invite
        try:
            user_member = ServerMember.objects.get(server=invite.server, user=request.user)
            # Only the invite creator, admins, or the server owner can delete invites
            if invite.created_by != request.user and not user_member.has_permission('manage_server'):
                return Response({'error': 'You do not have permission to delete this invite'}, status=status.HTTP_403_FORBIDDEN)
        except ServerMember.DoesNotExist:
            return Response({'error': 'You are not a member of this server'}, status=status.HTTP_403_FORBIDDEN)

        # Delete the invite
        invite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# Join Server by Invite Code
class JoinServerByInviteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Join a server using an invite code
        """
        # Get the invite code
        code = request.data.get('code')
        if not code:
            return Response({'error': 'Invite code is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Find the invite
        try:
            invite = ServerInvite.objects.get(code=code)
        except ServerInvite.DoesNotExist:
            return Response({'error': 'Invalid invite code'}, status=status.HTTP_404_NOT_FOUND)

        # Check if the invite is valid
        if not invite.is_valid():
            return Response({'error': 'This invite has expired or reached its maximum uses'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if user is already a member of the server
        if ServerMember.objects.filter(server=invite.server, user=request.user).exists():
            return Response({'error': 'You are already a member of this server'}, status=status.HTTP_400_BAD_REQUEST)

        # Add user to server
        member = ServerMember.objects.create(
            server=invite.server,
            user=request.user,
            role='member'
        )

        # Increment the invite uses
        invite.uses += 1
        invite.save()

        # Return the server details
        server_serializer = ServerSerializer(invite.server)
        return Response({
            'message': f'You have joined {invite.server.name}',
            'server': server_serializer.data
        }, status=status.HTTP_201_CREATED)

# Channel Views
class ChannelViewSet(viewsets.ModelViewSet):
    serializer_class = ChannelSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        server_id = self.kwargs.get('server_id')
        if server_id:
            server = get_object_or_404(Servers, server_id=server_id)

            # Check if user is a member of the server
            is_member = ServerMember.objects.filter(server=server, user=self.request.user).exists()
            is_owner = server.owner_id == self.request.user

            if not (is_member or is_owner):
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

# Direct Message Channels View
class DirectMessageChannelsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Get all direct message channels for the current user.
        This is a special endpoint to handle the @me route in the frontend.
        """
        # Get all DM channels where the current user is either user1 or user2
        dm_channels = DirectMessageChannel.objects.filter(
            Q(user1=request.user) | Q(user2=request.user)
        ).order_by('-last_message_at')

        # Serialize the channels
        serializer = DirectMessageChannelSerializer(dm_channels, many=True)
        return Response(serializer.data)

    def post(self, request):
        """
        Create a new direct message channel with another user.
        """
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({"error": "User ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            other_user = Users.objects.get(user_id=user_id)
        except Users.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        # Check if users are friends
        are_friends = Friends.objects.filter(
            (Q(users_id=request.user) & Q(user_friend_id=other_user)) |
            (Q(users_id=other_user) & Q(user_friend_id=request.user))
        ).exists()

        if not are_friends:
            return Response({"error": "You can only message users who are your friends"},
                           status=status.HTTP_403_FORBIDDEN)

        # Check if a DM channel already exists between these users
        existing_channel = DirectMessageChannel.objects.filter(
            (Q(user1=request.user) & Q(user2=other_user)) |
            (Q(user1=other_user) & Q(user2=request.user))
        ).first()

        if existing_channel:
            serializer = DirectMessageChannelSerializer(existing_channel)
            return Response(serializer.data)

        # Create a new DM channel
        dm_channel = DirectMessageChannel.objects.create(
            user1=request.user,
            user2=other_user
        )

        serializer = DirectMessageChannelSerializer(dm_channel)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

# Direct Message with Specific User View
class DirectMessageUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        """
        Get direct messages between the current user and the specified user.
        """
        try:
            other_user = Users.objects.get(user_id=user_id)
        except Users.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        # Find the DM channel between these users
        dm_channel = DirectMessageChannel.objects.filter(
            (Q(user1=request.user) & Q(user2=other_user)) |
            (Q(user1=other_user) & Q(user2=request.user))
        ).first()

        if not dm_channel:
            return Response({"error": "No direct message channel exists with this user"},
                           status=status.HTTP_404_NOT_FOUND)

        # Get messages in this channel
        messages = UserMessages.objects.filter(dm_channel=dm_channel).order_by('time_stamp')
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)

    def post(self, request, user_id):
        """
        Send a direct message to the specified user.
        """
        try:
            other_user = Users.objects.get(user_id=user_id)
        except Users.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        # Find or create the DM channel between these users
        dm_channel, created = DirectMessageChannel.objects.get_or_create(
            user1=request.user if request.user.user_id < other_user.user_id else other_user,
            user2=other_user if request.user.user_id < other_user.user_id else request.user,
            defaults={'last_message_at': timezone.now()}
        )

        # Create the message
        content = request.data.get('content')
        if not content:
            return Response({"error": "Message content is required"}, status=status.HTTP_400_BAD_REQUEST)

        message = UserMessages.objects.create(
            dm_channel=dm_channel,
            user_channel_id=request.user,
            content=content,
            attachment_url=request.data.get('attachment_url'),
            attachment_type=request.data.get('attachment_type')
        )

        # Update the last_message_at timestamp
        dm_channel.last_message_at = timezone.now()
        dm_channel.save()

        # Create notification for the other user
        Notifications.objects.create(
            user_id=other_user,
            notification_type='message',
            message=message,
            title='New Direct Message',
            content=f'{request.user.username} sent you a message'
        )

        serializer = MessageSerializer(message)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

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
            is_member = ServerMember.objects.filter(server=server, user=self.request.user).exists()
            is_owner = server.owner_id == self.request.user

            if not (is_member or is_owner):
                return UserMessages.objects.none()

            return UserMessages.objects.filter(message_channel_id=channel).order_by('time_stamp')
        return UserMessages.objects.none()

    def perform_create(self, serializer):
        channel_id = self.kwargs.get('channel_id')
        channel = get_object_or_404(Channels, channel_id=channel_id)

        # Check if user has access to this channel
        server = channel.discord_server_id
        is_member = ServerMember.objects.filter(server=server, user=self.request.user).exists()
        is_owner = server.owner_id == self.request.user

        if not (is_member or is_owner):
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


# User Browse View
class UserBrowseView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Get a list of all users for browsing and adding friends.
        Excludes the current user and users who are already friends.
        """
        # Get current user's friends
        friends = Friends.objects.filter(users_id=request.user, status=True).values_list('user_friend_id', flat=True)

        # Get all users except current user and friends
        users = Users.objects.exclude(user_id=request.user.user_id).exclude(user_id__in=friends)

        # Get blocked users
        blocked_users = BlockedUser.objects.filter(user=request.user).values_list('blocked_user', flat=True)
        users = users.exclude(user_id__in=blocked_users)

        # Check if there's a search query
        search_query = request.query_params.get('search', None)
        if search_query:
            users = users.filter(
                Q(username__icontains=search_query) |
                Q(display_name__icontains=search_query)
            )

        # Pagination
        page = request.query_params.get('page', 1)
        try:
            page = int(page)
        except ValueError:
            page = 1

        page_size = 20
        start = (page - 1) * page_size
        end = start + page_size

        # Get total count for pagination
        total_count = users.count()
        total_pages = (total_count + page_size - 1) // page_size

        # Slice the queryset for pagination
        users = users[start:end]

        # Serialize the users
        serializer = UserSerializer(users, many=True)

        # Return the paginated response
        return Response({
            'users': serializer.data,
            'pagination': {
                'total_count': total_count,
                'total_pages': total_pages,
                'current_page': page,
                'page_size': page_size
            }
        })

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
