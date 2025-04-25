from django.db import models
from django.utils import timezone
from servers.models import Servers
from users.models import Users

# Create your models here.
class Channels(models.Model):
    channel_id = models.AutoField(primary_key=True)
    discord_server_id = models.ForeignKey(Servers, on_delete=models.CASCADE, related_name='channels_set')
    name = models.CharField(max_length=100)
    channel_type = models.CharField(max_length=60, default='text')
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"#{self.name} ({self.discord_server_id.name})"

    class Meta:
        verbose_name = 'Channel'
        verbose_name_plural = 'Channels'

class DirectMessageChannel(models.Model):
    dm_channel_id = models.AutoField(primary_key=True)
    user1 = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='dm_channels_as_user1')
    user2 = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='dm_channels_as_user2')
    created_at = models.DateTimeField(default=timezone.now)
    last_message_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"DM: {self.user1.username} and {self.user2.username}"

    class Meta:
        verbose_name = 'Direct Message Channel'
        verbose_name_plural = 'Direct Message Channels'
        unique_together = [['user1', 'user2']]

    def get_other_user(self, user):
        """Get the other user in the conversation"""
        if user.user_id == self.user1.user_id:
            return self.user2
        return self.user1
