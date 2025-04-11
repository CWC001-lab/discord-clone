from django.db import models
from servers.models import Servers



# Create your models here.
class Channels(models.Model):
    channel_id = models.AutoField(primary_key=True)
    discord_server_id = models.ForeignKey(Servers,on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    channel_type = models.CharField(max_length=60)
    created_at = models.DateTimeField(auto_created=True)
