from django.contrib.auth.models import Group
from guardian.shortcuts import assign_perm

from utils.commands import BaseCommand

from ...enums import ServicePermissions
from ...models import Service


class Command(BaseCommand):
    help = (
        "Create the permission groups necessary for the existing Services "
        "and assign them the corresponding object permissions"
    )

    def handle(self, dry_run: bool = False, verbosity: int = 0, *args, **kwargs):
        self.setup_logging(verbosity)

        created = 0

        service_groups = Group.objects.all().values_list("name", flat=True)
        services = Service.objects.exclude(name__in=service_groups)
        available_permissions = ServicePermissions.values

        if dry_run:
            self.logger.info(f"Groups that will be created: {services.count()}")
            return

        for service in services:
            self.logger.info(f"Creating group for service: {service.name}")
            group = Group.objects.create(name=service.name)
            created += 1

            for permission in available_permissions:
                self.logger.info(f"Adding permission to group: {permission}")
                assign_perm(permission, group, service)

        self.stdout.write(self.style.SUCCESS(f"Groups created: {created}"))
