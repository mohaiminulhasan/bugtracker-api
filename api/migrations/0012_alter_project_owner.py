# Generated by Django 3.2 on 2021-05-09 20:07

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api', '0011_alter_ticket_developer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='owner',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='owned_projects', to=settings.AUTH_USER_MODEL),
        ),
    ]