# Generated by Django 5.1.7 on 2025-04-11 10:34

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Servers',
            fields=[
                ('created_at', models.DateTimeField(auto_created=True)),
                ('server_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('owner_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.users')),
            ],
        ),
    ]
