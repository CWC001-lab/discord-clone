from rest_framework import serializers
from users.models import Users
from servers.models import Servers, ServerMember, ServerRole, ServerInvite
from channels.models import Channels
from user_messages.models import UserMessages, MessageReaction
from friends.models import Friends, FriendRequest, BlockedUser
from notifications.models import Notifications
from .models import UserProfile

# User Serializers
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ['user_id', 'username', 'email', 'display_name', 'created_at']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        return Users.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )

class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = UserProfile
        fields = ['id', 'username', 'email', 'display_name', 'avatar', 'bio', 'date_of_birth', 'created_at', 'updated_at']

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = Users
        fields = ['username', 'email', 'password', 'confirm_password', 'display_name']

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match")
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        password = validated_data.pop('password')

        # Use the create_user method from the custom manager
        user = Users.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=password,
            display_name=validated_data.get('display_name', validated_data['username'])
        )
        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

# Channel Serializer
class ChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Channels
        fields = ['channel_id', 'name', 'channel_type', 'created_at']

# Server Role Serializer
class ServerRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServerRole
        fields = ['id', 'server', 'name', 'color', 'position', 'is_default',
                 'manage_channels', 'manage_server', 'manage_roles', 'manage_messages',
                 'kick_members', 'ban_members', 'create_invites',
                 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

# Server Invite Serializer
class ServerInviteSerializer(serializers.ModelSerializer):
    server_name = serializers.CharField(source='server.name', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    is_valid = serializers.BooleanField(read_only=True)

    class Meta:
        model = ServerInvite
        fields = ['id', 'server', 'server_name', 'code', 'created_by', 'created_by_username',
                 'max_uses', 'uses', 'expires_at', 'created_at', 'is_valid']
        read_only_fields = ['code', 'uses', 'created_at', 'is_valid']

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['is_valid'] = instance.is_valid()
        return ret

# Server Member Serializer
class ServerMemberSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    display_name = serializers.CharField(source='user.display_name', read_only=True)
    roles = ServerRoleSerializer(many=True, read_only=True)

    class Meta:
        model = ServerMember
        fields = ['id', 'server', 'user', 'username', 'display_name', 'nickname', 'role', 'roles', 'joined_at']
        read_only_fields = ['joined_at']

# Server Serializers
class ServerSerializer(serializers.ModelSerializer):
    channels = ChannelSerializer(many=True, read_only=True, source='channels_set')
    owner_username = serializers.CharField(source='owner_id.username', read_only=True)
    member_count = serializers.SerializerMethodField()
    roles_count = serializers.SerializerMethodField()
    invites_count = serializers.SerializerMethodField()

    class Meta:
        model = Servers
        fields = ['server_id', 'name', 'description', 'icon', 'owner_id', 'owner_username',
                 'is_public', 'invite_code', 'created_at', 'updated_at', 'channels',
                 'member_count', 'roles_count', 'invites_count']

    def get_member_count(self, obj):
        return ServerMember.objects.filter(server=obj).count()

    def get_roles_count(self, obj):
        return ServerRole.objects.filter(server=obj).count()

    def get_invites_count(self, obj):
        return ServerInvite.objects.filter(server=obj).count()

class ServerCreateSerializer(serializers.ModelSerializer):
    channels = serializers.ListField(
        child=serializers.CharField(max_length=100),
        write_only=True,
        required=False
    )

    class Meta:
        model = Servers
        fields = ['name', 'description', 'icon', 'is_public', 'channels']

    def create(self, validated_data):
        channels_data = validated_data.pop('channels', [])

        # Generate a unique invite code
        import uuid
        invite_code = str(uuid.uuid4())[:8]
        validated_data['invite_code'] = invite_code

        server = Servers.objects.create(**validated_data)

        # Create default general channel if no channels provided
        if not channels_data:
            channels_data = ['general']

        for channel_name in channels_data:
            Channels.objects.create(
                discord_server_id=server,
                name=channel_name,
                channel_type='text'
            )

        return server

# Message Serializers
class MessageReactionSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = MessageReaction
        fields = ['reaction_id', 'message', 'user', 'username', 'emoji', 'created_at']

class MessageSerializer(serializers.ModelSerializer):
    author = UserSerializer(source='user_channel_id', read_only=True)
    reactions = MessageReactionSerializer(many=True, read_only=True)

    class Meta:
        model = UserMessages
        fields = ['message_id', 'message_channel_id', 'author', 'content', 'attachment_url',
                 'attachment_type', 'is_edited', 'edited_at', 'is_pinned', 'reactions', 'time_stamp']

class MessageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserMessages
        fields = ['content', 'attachment_url', 'attachment_type']

# Friend Serializers
class FriendRequestSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(source='sender.username', read_only=True)
    sender_avatar = serializers.CharField(source='sender.avatar', read_only=True, allow_null=True)
    receiver_username = serializers.CharField(source='receiver.username', read_only=True)
    receiver_avatar = serializers.CharField(source='receiver.avatar', read_only=True, allow_null=True)

    class Meta:
        model = FriendRequest
        fields = ['request_id', 'sender', 'sender_username', 'sender_avatar',
                 'receiver', 'receiver_username', 'receiver_avatar',
                 'status', 'created_at', 'updated_at']
        read_only_fields = ['status', 'created_at', 'updated_at']

class FriendSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user_friend_id.username', read_only=True)
    display_name = serializers.CharField(source='user_friend_id.display_name', read_only=True)

    class Meta:
        model = Friends
        fields = ['friends_id', 'user_friend_id', 'username', 'display_name', 'status', 'created_at']

class BlockedUserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='blocked_user.username', read_only=True)

    class Meta:
        model = BlockedUser
        fields = ['block_id', 'blocked_user', 'username', 'created_at']

# Notification Serializers
class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notifications
        fields = ['notify_id', 'user_id', 'notification_type', 'message', 'friend_request',
                 'channel', 'server', 'title', 'content', 'is_read', 'time_stamp']
