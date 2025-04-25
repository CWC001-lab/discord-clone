# Generated manually

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
        ('servers', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ServerRole',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('color', models.CharField(default='#99AAB5', max_length=7)),
                ('position', models.IntegerField(default=0)),
                ('is_default', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('manage_channels', models.BooleanField(default=False)),
                ('manage_server', models.BooleanField(default=False)),
                ('manage_roles', models.BooleanField(default=False)),
                ('manage_messages', models.BooleanField(default=False)),
                ('kick_members', models.BooleanField(default=False)),
                ('ban_members', models.BooleanField(default=False)),
                ('create_invites', models.BooleanField(default=True)),
                ('server', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='roles', to='servers.servers')),
            ],
            options={
                'unique_together': {('server', 'name')},
                'ordering': ['-position'],
            },
        ),
        migrations.CreateModel(
            name='ServerInvite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=20, unique=True)),
                ('max_uses', models.IntegerField(default=0)),
                ('uses', models.IntegerField(default=0)),
                ('expires_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created_invites', to='users.users')),
                ('server', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invites', to='servers.servers')),
            ],
        ),
        migrations.AddField(
            model_name='servermember',
            name='roles',
            field=models.ManyToManyField(blank=True, related_name='members', to='servers.serverrole'),
        ),
        migrations.AlterField(
            model_name='servermember',
            name='server',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='server_members', to='servers.servers'),
        ),
        migrations.AlterField(
            model_name='servermember',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='server_memberships', to='users.users'),
        ),
    ]
