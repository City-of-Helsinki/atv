from uuid import uuid4

import factory

from services.tests.factories import ServiceFactory
from users.tests.factories import UserFactory

from ..models import Attachment, Document


class DocumentFactory(factory.django.DjangoModelFactory):
    service = factory.SubFactory(ServiceFactory)
    user = factory.SubFactory(UserFactory)
    transaction_id = factory.LazyFunction(uuid4)
    tos_function_id = factory.LazyFunction(lambda: str(uuid4()).replace("-", ""))
    tos_record_id = factory.LazyFunction(lambda: str(uuid4()).replace("-", ""))

    class Meta:
        model = Document


class AttachmentFactory(factory.django.DjangoModelFactory):
    document = factory.SubFactory(DocumentFactory)
    media_type = "application/pdf"
    file = factory.django.FileField(filename="document.pdf")

    class Meta:
        model = Attachment
