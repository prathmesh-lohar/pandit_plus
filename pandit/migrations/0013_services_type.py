# Generated by Django 5.1.1 on 2024-10-05 10:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pandit', '0012_booking_conform_date_booking_conform_time'),
    ]

    operations = [
        migrations.CreateModel(
            name='services_type',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('services_type', models.CharField(blank=True, default='', max_length=255, null=True)),
            ],
        ),
    ]
