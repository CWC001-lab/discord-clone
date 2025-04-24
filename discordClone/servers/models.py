from django.db import models
from users.models import Users

# Create your models here.
class Servers(models.Model):
    server_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    owner_id = models.ForeignKey(Users,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_created=True)
