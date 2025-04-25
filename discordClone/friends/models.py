from django.db import models
from django.utils import timezone
from users.models import Users

class FriendRequest(models.Model):
    request_id = models.AutoField(primary_key=True)
    sender = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='sent_friend_requests')
    receiver = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='received_friend_requests')
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('accepted', 'Accepted'),
            ('rejected', 'Rejected')
        ],
        default='pending'
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('sender', 'receiver')
        verbose_name = 'Friend Request'
        verbose_name_plural = 'Friend Requests'

    def __str__(self):
        return f"{self.sender.username} -> {self.receiver.username} ({self.status})"

class Friends(models.Model):
    friends_id = models.AutoField(primary_key=True)
    users_id = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='friend_requests')
    user_friend_id = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='friends')
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('users_id', 'user_friend_id')
        verbose_name = 'Friend'
        verbose_name_plural = 'Friends'

    def __str__(self):
        return f"{self.users_id.username} and {self.user_friend_id.username}"

class BlockedUser(models.Model):
    block_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='blocked_users')
    blocked_user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='blocked_by')
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('user', 'blocked_user')
        verbose_name = 'Blocked User'
        verbose_name_plural = 'Blocked Users'

    def __str__(self):
        return f"{self.user.username} blocked {self.blocked_user.username}"