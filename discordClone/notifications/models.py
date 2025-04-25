from django.db import models
from django.utils import timezone
from users.models import Users
from user_messages.models import UserMessages
from channels.models import Channels
from servers.models import Servers
from friends.models import FriendRequest

# Create your models here.
class Notifications(models.Model):
    notify_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='notifications')

    # Notification types
    NOTIFICATION_TYPES = [
        ('message', 'Message'),
        ('mention', 'Mention'),
        ('friend_request', 'Friend Request'),
        ('server_invite', 'Server Invite'),
        ('server_event', 'Server Event'),
    ]

    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)

    # Optional related objects
    message = models.ForeignKey(UserMessages, on_delete=models.CASCADE, null=True, blank=True)
    friend_request = models.ForeignKey(FriendRequest, on_delete=models.CASCADE, null=True, blank=True)
    channel = models.ForeignKey(Channels, on_delete=models.CASCADE, null=True, blank=True)
    server = models.ForeignKey(Servers, on_delete=models.CASCADE, null=True, blank=True)

    title = models.CharField(max_length=100)
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    time_stamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.notification_type} notification for {self.user_id.username}"

    class Meta:
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-time_stamp']
