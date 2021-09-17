import factory

from services.models import Service, ServiceAPIKey, ServiceClientId


class ServiceFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence(lambda n: "service %d" % n)

    @factory.lazy_attribute
    def description(self):
        return f"{self.name} description"

    class Meta:
        model = Service


class ServiceAPIKeyFactory(factory.django.DjangoModelFactory):
    service = factory.SubFactory(ServiceFactory)
    name = factory.Sequence(lambda n: "api key %d" % n)

    class Meta:
        model = ServiceAPIKey

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Use correct manager method for APIKey."""
        manager = cls._get_manager(model_class)
        obj, key = manager.create_key(*args, **kwargs)
        return obj


class ServiceClientIdFactory(factory.django.DjangoModelFactory):
    service = factory.SubFactory(ServiceFactory)
    client_id = factory.Sequence(lambda n: "https://api.hel.fi/auth/sc-%d" % n)

    class Meta:
        model = ServiceClientId
