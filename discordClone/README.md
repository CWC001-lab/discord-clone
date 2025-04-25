# Discord Clone Backend

This is a streamlined Django backend for the Discord Clone project. The project has been optimized by removing unnecessary Django components and focusing only on the essential functionality needed for the API.

## Project Structure

The project consists of the following apps:

- `api`: Main API endpoints and authentication
- `channels`: Channel management
- `friends`: Friend relationships
- `user_messages`: Message handling
- `notifications`: User notifications
- `servers`: Server management
- `users`: User authentication and profiles

## Database Configuration

The project uses Supabase PostgreSQL with the following credentials (stored in .env):

```
DB_NAME=postgres
DB_USER=postgres.oxywhsmiozzqqmcxoijq
DB_PASSWORD=discordclone123
DB_HOST=aws-0-eu-central-1.pooler.supabase.com
DB_PORT=6543
```

## Frontend Connection

The backend is configured to accept requests from the frontend at:

```
FRONTEND_URL=http://localhost:3000
```

## Running the Project

To run the project:

1. Ensure you have the `.env` file with the database credentials
2. Run migrations: `py manage.py makemigrations` and `py manage.py migrate`
3. Run the server script: `run_server.bat` or `py manage.py runserver`
4. The API will be available at `http://localhost:8000/api/`

## API Documentation

### Authentication

#### Register

- **URL**: `/api/auth/register/`
- **Method**: `POST`
- **Request Body**:
  ```json
  {
    "username": "example_user",
    "email": "user@example.com",
    "password": "securepassword",
    "confirm_password": "securepassword",
    "display_name": "Example User"
  }
  ```
- **Response**: Returns user details and authentication token

#### Login

- **URL**: `/api/auth/login/`
- **Method**: `POST`
- **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "password": "securepassword"
  }
  ```
- **Response**: Returns user details and authentication token

#### Logout

- **URL**: `/api/auth/logout/`
- **Method**: `POST`
- **Authentication**: Required
- **Response**: Confirmation message

### User Profile

#### Get Profile

- **URL**: `/api/profile/`
- **Method**: `GET`
- **Authentication**: Required
- **Response**: Returns user profile details

#### Update Profile

- **URL**: `/api/profile/`
- **Method**: `PUT`
- **Authentication**: Required
- **Request Body**:
  ```json
  {
    "display_name": "New Display Name",
    "avatar": "https://example.com/avatar.jpg",
    "bio": "This is my bio"
  }
  ```
- **Response**: Returns updated profile

### Servers

#### List Servers

- **URL**: `/api/servers/`
- **Method**: `GET`
- **Authentication**: Required
- **Response**: Returns list of servers owned by the user

#### Create Server

- **URL**: `/api/servers/`
- **Method**: `POST`
- **Authentication**: Required
- **Request Body**:
  ```json
  {
    "name": "My Server",
    "channels": ["general", "random"]
  }
  ```
- **Response**: Returns created server details

#### Get Server Details

- **URL**: `/api/servers/{server_id}/`
- **Method**: `GET`
- **Authentication**: Required
- **Response**: Returns server details including channels

#### Update Server

- **URL**: `/api/servers/{server_id}/`
- **Method**: `PUT`
- **Authentication**: Required
- **Request Body**:
  ```json
  {
    "name": "Updated Server Name",
    "description": "This is my server"
  }
  ```
- **Response**: Returns updated server details

#### Delete Server

- **URL**: `/api/servers/{server_id}/`
- **Method**: `DELETE`
- **Authentication**: Required
- **Response**: No content

### Channels

#### List Channels

- **URL**: `/api/channels/{server_id}/`
- **Method**: `GET`
- **Authentication**: Required
- **Response**: Returns list of channels in the server

#### Create Channel

- **URL**: `/api/channels/{server_id}/`
- **Method**: `POST`
- **Authentication**: Required
- **Request Body**:
  ```json
  {
    "name": "new-channel",
    "channel_type": "text"
  }
  ```
- **Response**: Returns created channel details

#### Get Channel Details

- **URL**: `/api/channels/{server_id}/{channel_id}/`
- **Method**: `GET`
- **Authentication**: Required
- **Response**: Returns channel details

#### Update Channel

- **URL**: `/api/channels/{server_id}/{channel_id}/`
- **Method**: `PUT`
- **Authentication**: Required
- **Request Body**:
  ```json
  {
    "name": "updated-channel-name"
  }
  ```
- **Response**: Returns updated channel details

#### Delete Channel

- **URL**: `/api/channels/{server_id}/{channel_id}/`
- **Method**: `DELETE`
- **Authentication**: Required
- **Response**: No content

### Messages

#### List Messages

- **URL**: `/api/messages/{channel_id}/`
- **Method**: `GET`
- **Authentication**: Required
- **Response**: Returns list of messages in the channel

#### Create Message

- **URL**: `/api/messages/{channel_id}/`
- **Method**: `POST`
- **Authentication**: Required
- **Request Body**:
  ```json
  {
    "content": "Hello, world!",
    "attachment_url": "https://example.com/image.jpg",
    "attachment_type": "image"
  }
  ```
- **Response**: Returns created message details

#### Get Message Details

- **URL**: `/api/messages/{channel_id}/{message_id}/`
- **Method**: `GET`
- **Authentication**: Required
- **Response**: Returns message details

#### Update Message

- **URL**: `/api/messages/{channel_id}/{message_id}/`
- **Method**: `PUT`
- **Authentication**: Required
- **Request Body**:
  ```json
  {
    "content": "Updated message content"
  }
  ```
- **Response**: Returns updated message details

#### Delete Message

- **URL**: `/api/messages/{channel_id}/{message_id}/`
- **Method**: `DELETE`
- **Authentication**: Required
- **Response**: No content

#### React to Message

- **URL**: `/api/messages/{channel_id}/{message_id}/react/`
- **Method**: `POST`
- **Authentication**: Required
- **Request Body**:
  ```json
  {
    "emoji": "👍"
  }
  ```
- **Response**: Returns reaction details or confirmation of removal

### Friends

#### List Friends

- **URL**: `/api/friends/`
- **Method**: `GET`
- **Authentication**: Required
- **Response**: Returns list of friends

#### List Friend Requests

- **URL**: `/api/friend-requests/`
- **Method**: `GET`
- **Authentication**: Required
- **Response**: Returns list of friend requests

#### Send Friend Request

- **URL**: `/api/friend-requests/`
- **Method**: `POST`
- **Authentication**: Required
- **Request Body**:
  ```json
  {
    "receiver": "user_id"
  }
  ```
- **Response**: Returns created friend request details

#### Accept Friend Request

- **URL**: `/api/friend-requests/{request_id}/accept/`
- **Method**: `POST`
- **Authentication**: Required
- **Response**: Confirmation message

#### Reject Friend Request

- **URL**: `/api/friend-requests/{request_id}/reject/`
- **Method**: `POST`
- **Authentication**: Required
- **Response**: Confirmation message

### Blocked Users

#### List Blocked Users

- **URL**: `/api/blocked-users/`
- **Method**: `GET`
- **Authentication**: Required
- **Response**: Returns list of blocked users

#### Block User

- **URL**: `/api/blocked-users/`
- **Method**: `POST`
- **Authentication**: Required
- **Request Body**:
  ```json
  {
    "blocked_user": "user_id"
  }
  ```
- **Response**: Returns blocked user details

#### Unblock User

- **URL**: `/api/blocked-users/{block_id}/`
- **Method**: `DELETE`
- **Authentication**: Required
- **Response**: No content

### Notifications

#### List Notifications

- **URL**: `/api/notifications/`
- **Method**: `GET`
- **Authentication**: Required
- **Response**: Returns list of notifications

#### Mark Notification as Read

- **URL**: `/api/notifications/{notification_id}/mark_read/`
- **Method**: `POST`
- **Authentication**: Required
- **Response**: Confirmation message

#### Mark All Notifications as Read

- **URL**: `/api/notifications/mark_all_read/`
- **Method**: `POST`
- **Authentication**: Required
- **Response**: Confirmation message

## Authentication

All API endpoints (except registration and login) require authentication using Token Authentication. Include the token in the request header:

```
Authorization: Token <your_token>
```
