from django.db import models
from channels.models import Channels
from users.models import Users


# Create your models here.
class UserMessages(models.Model):
    message_id = models.AutoField(primary_key=True)
    message_channel_id = models.ForeignKey(Channels,on_delete=models.CASCADE)
    user_channel_id = models.ForeignKey(Users,on_delete=models.CASCADE)
    content = models.CharField(max_length=100)
    time_stamp = models.DateTimeField(auto_created=True)