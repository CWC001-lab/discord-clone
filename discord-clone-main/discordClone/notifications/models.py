from django.db import models
from users.models import Users
from user_messages.models import UserMessages

# Create your models here.
class Notifications(models.Model):
    notify_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(Users,on_delete=models.CASCADE)
    message = models.ForeignKey(UserMessages,on_delete=models.CASCADE)
    is_read = models.BooleanField(False)
    time_stamp = models.DateTimeField(auto_created=True)
