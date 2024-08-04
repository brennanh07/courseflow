# Generated by Django 5.0.7 on 2024-08-02 22:18

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Professor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('department', models.CharField(max_length=100)),
                ('rating', models.FloatField()),
                ('difficulty_level', models.FloatField()),
                ('would_take_again', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('abbreviation', models.CharField(max_length=100)),
                ('title', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('password', models.CharField(max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_login', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Section',
            fields=[
                ('crn', models.IntegerField(primary_key=True, serialize=False)),
                ('course', models.CharField(max_length=100)),
                ('class_type', models.CharField(max_length=100)),
                ('modality', models.CharField(max_length=100)),
                ('credit_hours', models.IntegerField()),
                ('capacity', models.IntegerField()),
                ('location', models.CharField(max_length=100)),
                ('exam_code', models.CharField(max_length=100)),
                ('professor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='scheduler.professor')),
            ],
        ),
        migrations.CreateModel(
            name='SectionTime',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('days', models.CharField(max_length=100)),
                ('begin_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('crn', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='scheduler.section')),
            ],
        ),
        migrations.CreateModel(
            name='ScheduleLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('crns', models.JSONField()),
                ('score', models.FloatField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='scheduler.user')),
            ],
        ),
        migrations.CreateModel(
            name='Schedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('crns', models.JSONField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('score', models.FloatField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='scheduler.user')),
            ],
        ),
        migrations.CreateModel(
            name='Preference',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tod_preference', models.CharField(max_length=100)),
                ('dow_preference', models.CharField(max_length=100)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='scheduler.user')),
            ],
        ),
        migrations.CreateModel(
            name='Weight',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tod_weight', models.FloatField()),
                ('dow_weight', models.FloatField()),
                ('prof_weight', models.FloatField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='scheduler.user')),
            ],
        ),
    ]
