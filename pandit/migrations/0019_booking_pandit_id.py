# Generated by Django 5.1.1 on 2024-10-06 13:01

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pandit', '0018_pandit_service_type_of_pooja'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='pandit_id',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='pandit_id', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]
