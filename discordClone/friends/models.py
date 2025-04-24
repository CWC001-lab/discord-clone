from django.db import models
from users.models import Users

class Friends(models.Model):
    friends_id = models.AutoField(primary_key=True)
    users_id = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='friend_requests')
    user_friend_id = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='friends')
    status = models.BooleanField(default=True)  # Use default=True for a boolean field