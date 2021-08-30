# Generated by Django 3.2.3 on 2021-06-28 12:06

import django.contrib.postgres.indexes
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("documents", "0001_initial"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="document",
            index=models.Index(fields=["created_at"], name="document_created_at_idx"),
        ),
        migrations.AddIndex(
            model_name="document",
            index=models.Index(fields=["updated_at"], name="document_updated_at_idx"),
        ),
        migrations.AddIndex(
            model_name="document",
            index=models.Index(fields=["business_id"], name="document_business_id_idx"),
        ),
        migrations.AddIndex(
            model_name="document",
            index=models.Index(
                fields=["transaction_id"], name="document_transaction_id_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="document",
            index=models.Index(fields=["draft"], name="document_draft_idx"),
        ),
        migrations.AddIndex(
            model_name="document",
            index=models.Index(
                fields=["locked_after"], name="document_locked_after_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="document",
            index=django.contrib.postgres.indexes.GinIndex(
                fields=["metadata"], name="document_metadata_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="document",
            index=models.Index(fields=["status"], name="document_status_idx"),
        ),
        migrations.AddIndex(
            model_name="document",
            index=models.Index(fields=["type"], name="document_type_idx"),
        ),
    ]