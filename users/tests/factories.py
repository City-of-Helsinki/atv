import factory
from django.contrib.auth import get_user_model


class UserFactory(factory.django.DjangoModelFactory):
    uuid = factory.Faker("uuid4")

    class Meta:
        model = get_user_model()
