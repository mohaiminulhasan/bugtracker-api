# Generated by Django 3.2 on 2021-04-30 19:02

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api', '0009_remove_ticket_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='admins',
            field=models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='project',
            name='users',
            field=models.ManyToManyField(blank=True, related_name='teams', to=settings.AUTH_USER_MODEL),
        ),
    ]