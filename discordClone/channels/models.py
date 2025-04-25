from django.db import models
from django.utils import timezone
from servers.models import Servers

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
