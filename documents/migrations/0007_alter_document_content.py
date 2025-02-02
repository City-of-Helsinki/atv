# Generated by Django 3.2.9 on 2022-05-03 08:33

from django.db import migrations

import documents.models


class Migration(migrations.Migration):
    dependencies = [
        ("documents", "0006_document_status_timestamp"),
    ]

    operations = [
        migrations.AlterField(
            model_name="document",
            name="content",
            field=documents.models.EncryptedJSONField(
                blank=True, default=dict, help_text="Encrypted content of the document."
            ),
        ),
    ]
