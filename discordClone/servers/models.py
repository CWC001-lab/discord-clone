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
    is_public = models.BooleanField(default=True)
    invite_code = models.CharField(max_length=20, blank=True, null=True, unique=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Server'
        verbose_name_plural = 'Servers'

    def generate_invite_code(self):
        """Generate a new invite code for the server"""
        import uuid
        self.invite_code = str(uuid.uuid4())[:8]
        self.save(update_fields=['invite_code'])
        return self.invite_code

class ServerRole(models.Model):
    """Custom roles for a server"""
    server = models.ForeignKey(Servers, on_delete=models.CASCADE, related_name='roles')
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=7, default="#99AAB5")  # Hex color code
    position = models.IntegerField(default=0)  # Higher position = higher in hierarchy
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    # Permissions
    manage_channels = models.BooleanField(default=False)
    manage_server = models.BooleanField(default=False)
    manage_roles = models.BooleanField(default=False)
    manage_messages = models.BooleanField(default=False)
    kick_members = models.BooleanField(default=False)
    ban_members = models.BooleanField(default=False)
    create_invites = models.BooleanField(default=True)

    class Meta:
        unique_together = ('server', 'name')
        ordering = ['-position']

    def __str__(self):
        return f"{self.name} in {self.server.name}"

class ServerInvite(models.Model):
    """Invites to join a server"""
    server = models.ForeignKey(Servers, on_delete=models.CASCADE, related_name='invites')
    code = models.CharField(max_length=20, unique=True)
    created_by = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='created_invites')
    max_uses = models.IntegerField(default=0)  # 0 = unlimited
    uses = models.IntegerField(default=0)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def is_expired(self):
        """Check if the invite is expired"""
        if self.expires_at is None:
            return False
        return timezone.now() > self.expires_at

    def is_valid(self):
        """Check if the invite is still valid"""
        if self.is_expired():
            return False
        if self.max_uses > 0 and self.uses >= self.max_uses:
            return False
        return True

    def __str__(self):
        return f"Invite {self.code} for {self.server.name}"

class ServerMember(models.Model):
    server = models.ForeignKey(Servers, on_delete=models.CASCADE, related_name='server_members')
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='server_memberships')
    nickname = models.CharField(max_length=100, blank=True, null=True)
    roles = models.ManyToManyField(ServerRole, related_name='members', blank=True)
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

    def has_permission(self, permission):
        """Check if the member has a specific permission"""
        # Owner has all permissions
        if self.role == 'owner':
            return True

        # Admin has all permissions except server ownership
        if self.role == 'admin' and permission != 'manage_server':
            return True

        # Check custom role permissions
        for role in self.roles.all():
            if getattr(role, permission, False):
                return True

        # Moderator has specific permissions
        if self.role == 'moderator':
            mod_permissions = ['manage_messages', 'kick_members', 'create_invites']
            if permission in mod_permissions:
                return True

        # All members can create invites by default
        if permission == 'create_invites':
            return True

        return False

    def __str__(self):
        return f"{self.user.username} in {self.server.name}"
