from helusers.models import AbstractUser


class User(AbstractUser):
    audit_log_id_field = "uuid"
