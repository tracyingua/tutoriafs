# Generated by Django 5.0.4 on 2025-05-04 12:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tutoria_app', '0024_alter_tutorschedule_balance_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='tutorsession',
            name='is_substitute',
            field=models.BooleanField(default=False, help_text='Whether this session was taught by a substitute tutor'),
        ),
        migrations.AddField(
            model_name='tutorsession',
            name='substitute_barangay',
            field=models.CharField(blank=True, help_text='Barangay of substitute tutor', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='tutorsession',
            name='substitute_contact',
            field=models.CharField(blank=True, help_text='Contact number of substitute tutor', max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='tutorsession',
            name='substitute_name',
            field=models.CharField(blank=True, help_text='Name of substitute tutor', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='tutorsession',
            name='substitute_street',
            field=models.CharField(blank=True, help_text='Street address of substitute tutor', max_length=100, null=True),
        ),
    ]
