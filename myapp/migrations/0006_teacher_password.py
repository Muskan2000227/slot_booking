# Generated by Django 5.0.7 on 2025-03-09 16:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("myapp", "0005_adminregister_alter_slot_end_time"),
    ]

    operations = [
        migrations.AddField(
            model_name="teacher",
            name="password",
            field=models.CharField(default=1, max_length=40),
            preserve_default=False,
        ),
    ]
