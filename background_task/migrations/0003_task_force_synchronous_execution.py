# Generated by Django 3.0 on 2021-03-10 07:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('background_task', '0002_auto_20170927_1109'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='force_synchronous_execution',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
    ]
