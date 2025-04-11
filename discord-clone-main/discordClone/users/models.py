from django.db import models

# Create your models here.
class Users(models.Model):
    user_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    password_hash = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_created=True)
