import ipaddress
import re
from contextlib import contextmanager
from copy import copy
from typing import Optional, Union

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.db import transaction
from django.db.models import Model
from django.db.models.base import ModelBase
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.viewsets import ModelViewSet

from audit_log import audit_logging
from audit_log.enums import Operation, Status
from services.utils import get_service_from_request

User = get_user_model()


class AuditLoggingModelViewSet(ModelViewSet):
    method_to_operation = {
        "POST": Operation.CREATE,
        "GET": Operation.READ,
        "PUT": Operation.UPDATE,
        "PATCH": Operation.UPDATE,
        "DELETE": Operation.DELETE,
    }
    created_instance: Optional[Model] = None

    def permission_denied(self, request, message=None, code=None):
        audit_logging.log(
            self._get_actor(),
            self._get_actor_backend(),
            self._get_operation(),
            self._get_target(),
            Status.FORBIDDEN,
            ip_address=self._get_ip_address(),
            service=get_service_from_request(request, raise_exception=False),
        )
        super().permission_denied(request, message, code)

    def list(self, request, *args, **kwargs):
        with self.record_action():
            return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        with self.record_action():
            return super().retrieve(request, *args, **kwargs)

    @transaction.atomic
    def perform_create(self, serializer):
        with self.record_action():
            super().perform_create(serializer)
            self.created_instance = serializer.instance

    @transaction.atomic
    def perform_update(self, serializer):
        with self.record_action():
            super().perform_update(serializer)

    @transaction.atomic
    def perform_destroy(self, instance):
        target = copy(instance)  # Will be destroyed, so we must save it
        with self.record_action(target=target):
            super().perform_destroy(instance)

    @contextmanager
    def record_action(self, target: Optional[Model] = None):
        """
        This context manager will run the managed code in a transaction and writes
        a new audit log entry in the same transaction. If an exception is raised,
        the transaction will be rolled back. If the user has no permission to perform
        the given action, a "FORBIDDEN" audit log event will be recorded.
        """
        actor = copy(self._get_actor())  # May be destroyed if actor is also the target
        actor_backend = self._get_actor_backend()
        operation = self._get_operation()
        service = get_service_from_request(self.request, raise_exception=False)
        try:
            with transaction.atomic():
                yield
                audit_logging.log(
                    actor,
                    actor_backend,
                    operation,
                    target or self._get_target(),
                    ip_address=self._get_ip_address(),
                    service=service,
                )
        except (NotAuthenticated, PermissionDenied):
            audit_logging.log(
                actor,
                actor_backend,
                operation,
                target or self._get_target(),
                Status.FORBIDDEN,
                ip_address=self._get_ip_address(),
                service=service,
            )
            raise

    def _get_actor(self) -> Union[User, AnonymousUser]:
        return self.request.user

    def _get_actor_backend(self) -> str:
        return self.request.session.get("_auth_user_backend", "")

    def _get_operation(self) -> Operation:
        return self.method_to_operation.get(self.request.method, Operation.READ)

    def _get_target(self) -> Optional[Union[Model, ModelBase]]:
        target = None
        lookup_value = self.kwargs.get(self.lookup_field, None)
        if lookup_value is not None:
            target = (
                self.get_queryset()
                .model.objects.filter(**{self.lookup_field: lookup_value})
                .first()
            )
        return target or self.created_instance or self.get_queryset().model

    def _get_ip_address(self) -> str:
        if settings.USE_X_FORWARDED_FOR:
            forwarded_for = [
                ip.strip()
                for ip in self.request.META.get("HTTP_X_FORWARDED_FOR", "").split(",")
            ]
            for ip in forwarded_for:
                try:
                    # This regexp matches IPv4 addresses without including the port number
                    regexp_for_ipv4 = re.match(
                        r"(^((25[0-5]|(2[0-4]|1\d|[1-9]|)\d)\.?\b){4})", ip
                    )
                    if ipaddress.ip_address(
                        regexp_for_ipv4[0] if regexp_for_ipv4 else ip
                    ).is_global:
                        return regexp_for_ipv4[0] if regexp_for_ipv4 else ip
                except ValueError:
                    continue

        return self.request.META.get("REMOTE_ADDR")
