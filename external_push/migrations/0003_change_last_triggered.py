# Generated by Django 3.0.13 on 2021-03-25 13:11

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('external_push', '0002_brewfather_updates'),
    ]

    operations = [
        migrations.AlterField(
            model_name='brewersfriendpushtarget',
            name='last_triggered',
            field=models.DateTimeField(default=django.utils.timezone.now, help_text='The last time we pushed data to this target'),
        ),
        migrations.AlterField(
            model_name='brewfatherpushtarget',
            name='last_triggered',
            field=models.DateTimeField(default=django.utils.timezone.now, help_text='The last time we pushed data to this target'),
        ),
        migrations.AlterField(
            model_name='genericpushtarget',
            name='last_triggered',
            field=models.DateTimeField(default=django.utils.timezone.now, help_text='The last time we pushed data to this target'),
        ),
        migrations.AlterField(
            model_name='grainfatherpushtarget',
            name='last_triggered',
            field=models.DateTimeField(default=django.utils.timezone.now, help_text='The last time we pushed data to this target'),
        ),
        migrations.AlterField(
            model_name='thingspeakpushtarget',
            name='last_triggered',
            field=models.DateTimeField(default=django.utils.timezone.now, help_text='The last time we pushed data to this target'),
        ),
    ]