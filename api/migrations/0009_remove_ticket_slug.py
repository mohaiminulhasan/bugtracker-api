# Generated by Django 3.2 on 2021-04-30 08:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_ticket_slug'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ticket',
            name='slug',
        ),
    ]
