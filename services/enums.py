from django.db.models import TextChoices


class ServicePermissions(TextChoices):
    MANAGE_DOCUMENTS = "can_manage_documents", "Can manage documents"
    VIEW_DOCUMENTS = "can_view_documents", "Can view documents"
    MANAGE_ATTACHMENTS = "can_manage_attachments", "Can manage attachments"
    VIEW_ATTACHMENTS = "can_view_attachments", "Can view attachments"
