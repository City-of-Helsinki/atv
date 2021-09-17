import factory
from django.contrib.auth.models import Group


class GroupFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence(lambda n: "group-%d" % n)

    class Meta:
        model = Group
        django_get_or_create = ("name",)
