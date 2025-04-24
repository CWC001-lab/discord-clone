# Discord Clone Backend

This is a streamlined Django backend for the Discord Clone project. The project has been optimized by removing unnecessary Django components and focusing only on the essential functionality needed for the API.

## Optimizations Made

1. **Removed Django Admin**
   - Removed admin site URLs
   - Removed admin app from INSTALLED_APPS
   - Cleaned up admin.py files in all apps

2. **Minimized Django Dependencies**
   - Kept only essential Django apps (auth, contenttypes, sessions)
   - Removed messages and staticfiles apps
   - Simplified middleware configuration

3. **Streamlined Settings**
   - Simplified template configuration
   - Reduced password validators to just minimum length
   - Cleaned up database configuration
   - Removed commented-out code

4. **Focused on API Functionality**
   - Maintained all REST Framework settings
   - Preserved CORS configuration for frontend communication
   - Kept token authentication intact

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
2. Run the server script: `run_server.bat`
3. The API will be available at `http://localhost:8000/api/`
