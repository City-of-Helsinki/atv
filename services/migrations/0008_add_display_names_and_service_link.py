# Generated by Django 3.2.16 on 2023-05-15 12:04

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("services", "0007_alter_id_and_hashedkey_max_length"),
    ]

    operations = [
        migrations.AddField(
            model_name="service",
            name="display_names",
            field=models.JSONField(
                blank=True,
                default=dict,
                help_text="Json structure containing display names for service",
            ),
        ),
        migrations.AddField(
            model_name="service",
            name="service_link",
            field=models.URLField(blank=True, help_text="Link to service's website"),
        ),
    ]