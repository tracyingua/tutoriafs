# Generated by Django 5.0.4 on 2025-04-27 22:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tutoria_app', '0013_alter_tutorschedule_paid_amount'),
    ]

    operations = [
        migrations.AddField(
            model_name='tutorsession',
            name='cancellation_reason',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='tutorsession',
            name='cancelled_by',
            field=models.CharField(blank=True, choices=[('tutor', 'Tutor'), ('parent', 'Parent')], max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='tutorsession',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('confirmed', 'Confirmed'), ('completed', 'Completed'), ('declined', 'Declined'), ('canceled', 'Canceled'), ('canceled_by_parent', 'Canceled by Parent'), ('canceled_by_tutor', 'Canceled by Tutor'), ('withdrawn', 'Withdrawn')], default='pending', max_length=20),
        ),
    ]
