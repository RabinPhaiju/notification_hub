# Generated by Django 5.1.3 on 2024-12-12 02:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('offer', '0002_offer_subject'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='offer',
            name='email_template',
        ),
    ]
