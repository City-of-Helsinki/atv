from django_filters import rest_framework as filters

from ..models import Document


class DocumentFilterSet(filters.FilterSet):
    user_id = filters.UUIDFilter(field_name="user__uuid")
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
        fields = [
            "status",
            "type",
            "business_id",
            "transaction_id",
        ]
