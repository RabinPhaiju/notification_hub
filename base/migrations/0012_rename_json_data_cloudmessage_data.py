# Generated by Django 5.1.3 on 2024-12-09 01:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0011_cloudmessage_mailmessage'),
    ]

    operations = [
        migrations.RenameField(
            model_name='cloudmessage',
            old_name='json_data',
            new_name='data',
        ),
    ]
