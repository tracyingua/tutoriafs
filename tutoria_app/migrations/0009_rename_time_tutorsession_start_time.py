# Generated by Django 5.0.4 on 2025-04-27 18:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tutoria_app', '0008_alter_tutorsession_status'),
    ]

    operations = [
        migrations.RenameField(
            model_name='tutorsession',
            old_name='time',
            new_name='start_time',
        ),
    ]
