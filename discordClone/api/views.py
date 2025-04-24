import logging
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, AllowAny
from users.models import Users
from servers.models import Servers
from .models import UserProfile
from .serializers import (
    UserProfileSerializer,
    UserRegistrationSerializer,
    LoginSerializer,
    ServerSerializer,
    ServerCreateSerializer
)

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
