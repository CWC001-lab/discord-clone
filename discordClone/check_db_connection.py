import os
import sys
import time
import django
from django.conf import settings
from django.db import connections
from django.db.utils import OperationalError

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'discordClone.settings')
django.setup()

def check_database_connection(max_attempts=3, delay=2):
    """
    Check if the database connection is working.
    
    Args:
        max_attempts: Maximum number of connection attempts
        delay: Delay between attempts in seconds
        
    Returns:
        bool: True if connection successful, False otherwise
    """
    print("\n" + "="*50)
    print("CHECKING DATABASE CONNECTION")
    print("="*50)
    
    # Get database configuration
    db_name = settings.DATABASES['default']['NAME']
    db_host = settings.DATABASES['default']['HOST']
    db_port = settings.DATABASES['default']['PORT']
    
    print(f"Database: {db_name}")
    print(f"Host: {db_host}")
    print(f"Port: {db_port}")
    print("-"*50)
    
    for attempt in range(1, max_attempts + 1):
        try:
            print(f"Connection attempt {attempt}/{max_attempts}...")
            # Test the database connection
            connections['default'].ensure_connection()
            
            # If we get here, the connection is working
            print("\n✅ DATABASE CONNECTION SUCCESSFUL!")
            print(f"Successfully connected to PostgreSQL at {db_host}:{db_port}")
            print("="*50 + "\n")
            return True
            
        except OperationalError as e:
            print(f"❌ Connection failed: {str(e)}")
            if attempt < max_attempts:
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print("\n❌ DATABASE CONNECTION FAILED!")
                print(f"Could not connect to PostgreSQL at {db_host}:{db_port}")
                print("Please check your database credentials and network connection.")
                print("="*50 + "\n")
                return False
        except Exception as e:
            print(f"\n❌ Unexpected error: {str(e)}")
            print("="*50 + "\n")
            return False

if __name__ == "__main__":
    success = check_database_connection()
    sys.exit(0 if success else 1)
