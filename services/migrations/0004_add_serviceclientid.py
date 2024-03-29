# Generated by Django 3.2.7 on 2021-09-15 09:36

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("services", "0003_add_service_permissions"),
    ]

    operations = [
        migrations.CreateModel(
            name="ServiceClientId",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "client_id",
                    models.CharField(
                        help_text="Client ID of the OIDC token which identifies the used service.",
                        max_length=256,
                        unique=True,
                        verbose_name="client ID",
                    ),
                ),
                (
                    "service",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="client_ids",
                        to="services.service",
                        verbose_name="service",
                    ),
                ),
            ],
            options={
                "verbose_name": "client ID",
                "verbose_name_plural": "client IDs",
            },
        ),
    ]
