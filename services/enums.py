from django.db.models import TextChoices


class ServicePermissions(TextChoices):
    ADD_DOCUMENTS = "can_add_documents", "Can add documents"
    CHANGE_DOCUMENTS = "can_change_documents", "Can change documents"
    DELETE_DOCUMENTS = "can_delete_documents", "Can delete documents"
    VIEW_DOCUMENTS = "can_view_documents", "Can view documents"
    ADD_ATTACHMENTS = "can_add_attachments", "Can add attachments"
    CHANGE_ATTACHMENTS = "can_change_attachments", "Can change attachments"
    DELETE_ATTACHMENTS = "can_delete_attachments", "Can delete attachments"
    VIEW_ATTACHMENTS = "can_view_attachments", "Can view attachments"
