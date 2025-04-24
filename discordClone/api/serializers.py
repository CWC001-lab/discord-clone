from rest_framework import serializers
from users.models import Users
from servers.models import Servers
from channels.models import Channels
from .models import UserProfile
# No need to import make_password as we're using the model's methods

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ['user_id', 'username', 'email', 'password', 'created_at']
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
        fields = ['username', 'email', 'password', 'confirm_password']

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
            password=password
        )
        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

class ChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Channels
        fields = ['channel_id', 'name', 'channel_type', 'created_at']

class ServerSerializer(serializers.ModelSerializer):
    channels = ChannelSerializer(many=True, read_only=True, source='channels_set')

    class Meta:
        model = Servers
        fields = ['server_id', 'name', 'owner_id', 'created_at', 'channels']

class ServerCreateSerializer(serializers.ModelSerializer):
    channels = serializers.ListField(
        child=serializers.CharField(max_length=100),
        write_only=True,
        required=False
    )

    class Meta:
        model = Servers
        fields = ['name', 'channels']

    def create(self, validated_data):
        channels_data = validated_data.pop('channels', [])
        server = Servers.objects.create(**validated_data)

        for channel_name in channels_data:
            Channels.objects.create(
                discord_server_id=server,
                name=channel_name,
                channel_type='text'
            )

        return server
