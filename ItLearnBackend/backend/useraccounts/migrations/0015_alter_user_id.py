# Generated by Django 5.1.4 on 2025-01-08 12:53

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('useraccounts', '0014_alter_user_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='id',
            field=models.UUIDField(default=uuid.UUID('87049ff2-871d-4f04-8321-c4130aef47a5'), editable=False, primary_key=True, serialize=False),
        ),
    ]
