# Generated by Django 5.1.4 on 2025-01-06 16:43

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('useraccounts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='id',
            field=models.UUIDField(default=uuid.UUID('6efa3c8d-0526-48bc-8c99-4d5cf7dde79b'), editable=False, primary_key=True, serialize=False),
        ),
    ]
