from helusers.models import AbstractUser


class User(AbstractUser):
    audit_log_id_field = "uuid"

    def __str__(self):
        return f"{self.id} ({self.email or self.username or '-'})"
