# Generated by Django 5.1.1 on 2024-10-06 10:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pandit', '0015_booking_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='service_type',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
