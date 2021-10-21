import logging

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.utils.text import slugify
from guardian.shortcuts import assign_perm

from .models import Service, ServiceAPIKey

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Service, dispatch_uid="create_service_group")
def create_service_group(sender, instance: Service, created: bool, **kwargs):
    if created:
        group, _created = Group.objects.get_or_create(name=instance.name)
        logger.debug(f"Created permission group for service: {instance.name}")
        for perm in Service._meta.permissions:
            assign_perm(f"{perm[0]}", group, instance)
            logger.debug(f"Added permission to group: {perm[0]}")


@receiver(post_delete, sender=Service, dispatch_uid="remove_service_group")
def remove_service_group(sender, instance: Service, **kwargs):
    Group.objects.filter(name=instance.name).delete()
    logger.debug(f"Removed permission group: {instance.name}")


@receiver(post_save, sender=ServiceAPIKey, dispatch_uid="create_service_api_key_user")
def create_service_api_key_user(
    sender, instance: ServiceAPIKey, created: bool, **kwargs
):
    if created and not instance.user:
        user_model = get_user_model()
        username = slugify(f"service-api-key-{instance.service.name}-{instance.name}")
        user = user_model.objects.create_user(username=username)
        instance.user = user
        instance.save()
        logger.debug(
            f"Created user {user} for ServiceAPIKey {instance} permission group for service: {instance.name}"
        )
        for perm in Service._meta.permissions:
            assign_perm(f"{perm[0]}", user, instance.service)
            logger.debug(f"Added permission to group: {perm[0]}")
