# Generated by Django 5.1.4 on 2025-01-13 12:22

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('useraccounts', '0021_alter_user_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='id',
            field=models.UUIDField(default=uuid.UUID('26ee9252-caf4-439e-a28f-1c9907a6e4e7'), editable=False, primary_key=True, serialize=False),
        ),
    ]