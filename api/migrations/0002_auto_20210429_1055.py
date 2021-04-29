# Generated by Django 3.2 on 2021-04-29 10:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='tickethistory',
            options={'verbose_name_plural': 'Ticket histories'},
        ),
        migrations.AddField(
            model_name='project',
            name='slug',
            field=models.SlugField(default='demo-slug', max_length=255),
            preserve_default=False,
        ),
    ]