from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from users.models import Users

# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(Users, on_delete=models.CASCADE, related_name='profile')
    display_name = models.CharField(max_length=100, blank=True, null=True)
    avatar = models.URLField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s profile"

# Signal to create token when a user is created
@receiver(post_save, sender=Users)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    """
    Create a token and user profile when a new user is created

    Args:
        sender: The model class that sent the signal
        instance: The actual instance being saved
        created: Boolean indicating if this is a new instance
        kwargs: Additional keyword arguments
    """
    if created:
        try:
            # Create auth token
            Token.objects.get_or_create(user=instance)

            # Create user profile if it doesn't exist
            UserProfile.objects.get_or_create(
                user=instance,
                defaults={
                    'display_name': instance.username,
                }
            )
        except Exception as e:
            # Log the error
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error creating token or profile for user {instance.username}: {str(e)}")
