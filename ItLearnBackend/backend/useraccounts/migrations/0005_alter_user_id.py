# Generated by Django 5.1.4 on 2025-01-07 10:55

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('useraccounts', '0004_alter_user_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='id',
            field=models.UUIDField(default=uuid.UUID('c9ee895a-1ac8-46fb-8dcd-f9b90ff50ebb'), editable=False, primary_key=True, serialize=False),
        ),
    ]
