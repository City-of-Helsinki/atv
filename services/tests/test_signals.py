from django.contrib.auth.models import Group
from guardian.shortcuts import get_perms

from services.enums import ServicePermissions
from services.models import Service


def test_create_service_creates_group(service):
    group = Group.objects.filter(name=service.name).first()
    assert group is not None

    group_perms = get_perms(group, service)
    for permission in list(ServicePermissions):
        assert permission in group_perms


def test_remove_service_removes_group(service):
    service_id = service.id
    service.delete()

    assert not Service.objects.filter(id=service_id).exists()
    assert not Group.objects.filter(name=service.name).exists()
