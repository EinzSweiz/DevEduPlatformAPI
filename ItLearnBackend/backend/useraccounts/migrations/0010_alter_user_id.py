# Generated by Django 5.1.4 on 2025-01-07 17:32

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('useraccounts', '0009_alter_user_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='id',
            field=models.UUIDField(default=uuid.UUID('51254732-b9de-4e5b-b988-a16971b5f30a'), editable=False, primary_key=True, serialize=False),
        ),
    ]