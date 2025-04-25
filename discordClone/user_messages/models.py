from django.db import models
from django.utils import timezone
from channels.models import Channels, DirectMessageChannel
from users.models import Users


# Create your models here.
class UserMessages(models.Model):
    message_id = models.AutoField(primary_key=True)
    message_channel_id = models.ForeignKey(Channels, on_delete=models.CASCADE, related_name='messages', null=True, blank=True)
    dm_channel = models.ForeignKey(DirectMessageChannel, on_delete=models.CASCADE, related_name='messages', null=True, blank=True)
    user_channel_id = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='messages')
    content = models.TextField()
    attachment_url = models.URLField(blank=True, null=True)
    attachment_type = models.CharField(max_length=20, blank=True, null=True)
    is_edited = models.BooleanField(default=False)
    edited_at = models.DateTimeField(blank=True, null=True)
    is_pinned = models.BooleanField(default=False)
    mentions = models.ManyToManyField(Users, related_name='mentioned_in', blank=True)
    time_stamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        if self.message_channel_id:
            return f"{self.user_channel_id.username} in #{self.message_channel_id.name}: {self.content[:50]}"
        else:
            return f"{self.user_channel_id.username} in DM: {self.content[:50]}"

    class Meta:
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'
        ordering = ['time_stamp']

class MessageReaction(models.Model):
    reaction_id = models.AutoField(primary_key=True)
    message = models.ForeignKey(UserMessages, on_delete=models.CASCADE, related_name='reactions')
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='reactions')
    emoji = models.CharField(max_length=50)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('message', 'user', 'emoji')

    def __str__(self):
        return f"{self.user.username} reacted with {self.emoji} to message {self.message.message_id}"