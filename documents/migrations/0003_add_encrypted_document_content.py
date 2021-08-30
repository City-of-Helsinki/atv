# Generated by Django 3.2.3 on 2021-06-29 17:44

from django.db import migrations
import encrypted_fields.fields


class Migration(migrations.Migration):

    dependencies = [
        ("documents", "0002_add_indexes_to_document"),
    ]

    operations = [
        migrations.AddField(
            model_name="document",
            name="content",
            field=encrypted_fields.fields.EncryptedTextField(
                default="", help_text="Encrypted content of the document."
            ),
            preserve_default=False,
        ),
    ]