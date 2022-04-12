from django.db.models import TextField
from django.db.models.functions import Cast
from django_filters import CharFilter, Filter, rest_framework as filters
from django_filters.constants import EMPTY_VALUES
from rest_framework.exceptions import ValidationError

from utils import uuid

from ..models import Document


class UserUUIDFilter(CharFilter):
    """
    Allows filtering for null values in addition to valid UUID
    """

    def filter(self, qs, value):
        if value in EMPTY_VALUES:
            return qs
        elif value.lower() == "null":
            return qs.filter(user__isnull=True)
        try:
            value = uuid.UUID(value)
        except ValueError:
            raise ValidationError(detail={"Invalid UUID": ["Enter a valid UUID."]})

        lookup = "%s__%s" % (self.field_name, self.lookup_expr)
        qs = self.get_method(qs)(**{lookup: value})
        return qs


class MetadataJSONFilter(Filter):
    """
    Custom filter for free searching from metadata field.
    Cast json to text and annotate it to queryset for filtering
    """

    def filter(self, qs, value):
        if value in EMPTY_VALUES:
            return qs
        return qs.annotate(metatext=Cast("metadata", TextField())).filter(
            metatext__contains=value
        )


class DocumentMetadataFilterSet(filters.FilterSet):
    service_name = filters.CharFilter(
        field_name="service__name", label="Service's name"
    )
    created_before = filters.DateFilter(
        field_name="created_at", lookup_expr="lt", label="Created before"
    )
    created_after = filters.DateFilter(
        field_name="created_at", lookup_expr="gt", label="Created after"
    )
    updated_before = filters.DateFilter(
        field_name="updated_at", lookup_expr="lt", label="Updated before"
    )
    updated_after = filters.DateFilter(
        field_name="updated_at", lookup_expr="gt", label="Updated after"
    )

    class Meta:
        model = Document
        fields = ["status", "type"]


class DocumentFilterSet(DocumentMetadataFilterSet):
    user_id = UserUUIDFilter(field_name="user__uuid")
    lookfor = MetadataJSONFilter(field_name="metadata", label="Look for")

    class Meta:
        model = Document
        fields = [
            "status",
            "type",
            "business_id",
            "transaction_id",
        ]
