# Generated by Django 5.1.3 on 2024-12-09 01:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0004_alter_forumpost_options'),
    ]

    operations = [
        migrations.DeleteModel(
            name='ForumPost',
        ),
    ]
