# Generated by Django 3.2.6 on 2021-08-12 11:08

import django.db.models.deletion
from django.db import migrations, models

import documents.utils


class Migration(migrations.Migration):

    dependencies = [
        ("documents", "0003_add_encrypted_document_content"),
    ]

    operations = [
        migrations.CreateModel(
            name="Attachment",
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
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="created at"),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="updated at"),
                ),
                (
                    "media_type",
                    models.CharField(
                        default="",
                        help_text="The media type of the attachment.",
                        max_length=255,
                        verbose_name="media type",
                    ),
                ),
                (
                    "size",
                    models.PositiveIntegerField(
                        help_text="Size of the attachment in bytes.",
                        verbose_name="size",
                    ),
                ),
                (
                    "filename",
                    models.CharField(
                        help_text="The original filename of the attachment.",
                        max_length=255,
                        verbose_name="filename",
                    ),
                ),
                (
                    "file",
                    models.FileField(
                        help_text="Encrypted file.",
                        upload_to=documents.utils.get_attachment_file_path,
                        verbose_name="file",
                    ),
                ),
                (
                    "document",
                    models.ForeignKey(
                        help_text="Document to which the file is attached.",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="attachments",
                        to="documents.document",
                        verbose_name="attachment",
                    ),
                ),
            ],
            options={
                "verbose_name": "attachment",
                "verbose_name_plural": "attachments",
                "default_related_name": "attachments",
            },
        ),
    ]