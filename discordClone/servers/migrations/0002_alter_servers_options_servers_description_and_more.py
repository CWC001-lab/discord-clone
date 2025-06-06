# Generated by Django 5.1.7 on 2025-04-25 01:42

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('servers', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='servers',
            options={'verbose_name': 'Server', 'verbose_name_plural': 'Servers'},
        ),
        migrations.AddField(
            model_name='servers',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='servers',
            name='icon',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='servers',
            name='invite_code',
            field=models.CharField(blank=True, max_length=20, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='servers',
            name='is_public',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='servers',
            name='members',
            field=models.ManyToManyField(blank=True, related_name='joined_servers', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='servers',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='servers',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='servers',
            name='owner_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='owned_servers', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='ServerMember',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nickname', models.CharField(blank=True, max_length=100, null=True)),
                ('role', models.CharField(choices=[('owner', 'Owner'), ('admin', 'Admin'), ('moderator', 'Moderator'), ('member', 'Member')], default='member', max_length=20)),
                ('joined_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('server', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='servers.servers')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('server', 'user')},
            },
        ),
    ]
