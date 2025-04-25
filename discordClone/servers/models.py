from django.db import models
from django.utils import timezone
from users.models import Users

# Create your models here.
class Servers(models.Model):
    server_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    icon = models.URLField(blank=True, null=True)
    owner_id = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='owned_servers')
    members = models.ManyToManyField(Users, related_name='joined_servers', blank=True)
    is_public = models.BooleanField(default=False)
    invite_code = models.CharField(max_length=20, blank=True, null=True, unique=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Server'
        verbose_name_plural = 'Servers'

class ServerMember(models.Model):
    server = models.ForeignKey(Servers, on_delete=models.CASCADE)
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    nickname = models.CharField(max_length=100, blank=True, null=True)
    role = models.CharField(
        max_length=20,
        choices=[
            ('owner', 'Owner'),
            ('admin', 'Admin'),
            ('moderator', 'Moderator'),
            ('member', 'Member')
        ],
        default='member'
    )
    joined_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('server', 'user')

    def __str__(self):
        return f"{self.user.username} in {self.server.name}"
