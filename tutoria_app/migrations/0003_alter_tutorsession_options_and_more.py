# Generated by Django 5.0.4 on 2025-04-26 19:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tutoria_app', '0002_alter_tutorschedule_options_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='tutorsession',
            options={'ordering': ['date']},
        ),
        migrations.AlterUniqueTogether(
            name='tutorsession',
            unique_together={('tutor_schedule', 'date', 'subject')},
        ),
        migrations.AddField(
            model_name='tutorschedule',
            name='total_hours',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=6),
        ),
        migrations.AlterField(
            model_name='tutorsession',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='tutorsession',
            name='duration',
            field=models.DecimalField(decimal_places=2, help_text='Duration in hours (1-3 hours)', max_digits=4),
        ),
        migrations.RemoveField(
            model_name='tutorsession',
            name='end_time',
        ),
        migrations.RemoveField(
            model_name='tutorsession',
            name='start_time',
        ),
    ]
