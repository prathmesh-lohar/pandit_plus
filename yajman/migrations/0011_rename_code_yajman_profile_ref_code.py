# Generated by Django 5.1.1 on 2024-10-18 14:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yajman', '0010_yajman_profile_code'),
    ]

    operations = [
        migrations.RenameField(
            model_name='yajman_profile',
            old_name='code',
            new_name='ref_code',
        ),
    ]
