from helusers.models import AbstractUser


class User(AbstractUser):
    audit_log_id_field = "uuid"

    def __str__(self):
        return f"{self.id} ({self.email or self.username or '-'})"

    def clean(self):
        super().clean()
        # Prevent personal details from being saved to ATV user model, ATV doesn't need to know anything else than uuid
        self.first_name = self.last_name = self.email = ""

    class Meta:
        permissions = [("view_document_statistics", "Can view document statistics")]
