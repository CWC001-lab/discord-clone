# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('servers', '0003_merge_20250425_0718'),
    ]

    operations = [
        migrations.AlterField(
            model_name='servers',
            name='is_public',
            field=models.BooleanField(default=True),
        ),
    ]
