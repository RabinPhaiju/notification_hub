# Generated by Django 5.1.3 on 2024-12-13 08:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0017_rename_push_notification_usernotificationsetting_push'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='notification',
            name='category',
        ),
        migrations.AlterField(
            model_name='usernotificationsetting',
            name='subject',
            field=models.CharField(blank=True, choices=[('all', 'All'), ('new_offer', 'New Offer'), ('offer_reminder', 'Offer Reminder')], max_length=50, null=True),
        ),
    ]
