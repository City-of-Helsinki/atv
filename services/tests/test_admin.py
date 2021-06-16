from django.urls import reverse


def test_admin_service_list_view_query_count_not_too_big(
    admin_client, django_assert_max_num_queries, service_api_key_factory
):
    admin_view_url = reverse("admin:services_service_changelist")

    with django_assert_max_num_queries(10):
        admin_client.get(admin_view_url)

    service_api_key_factory.create_batch(11)

    with django_assert_max_num_queries(10):
        admin_client.get(admin_view_url)


def test_admin_service_api_key_list_view_query_count_not_too_big(
    admin_client, django_assert_max_num_queries, service_api_key_factory
):
    admin_view_url = reverse("admin:services_serviceapikey_changelist")

    with django_assert_max_num_queries(10):
        admin_client.get(admin_view_url)

    service_api_key_factory.create_batch(11)

    with django_assert_max_num_queries(10):
        admin_client.get(admin_view_url)


def test_admin_service_api_key_change_view_query_count_not_too_big(
    admin_client, django_assert_max_num_queries, service_api_key, service_factory
):
    admin_view_url = reverse(
        "admin:services_serviceapikey_change", args=(service_api_key.pk,)
    )

    with django_assert_max_num_queries(10):
        admin_client.get(admin_view_url)

    service_factory.create_batch(11)

    with django_assert_max_num_queries(10):
        admin_client.get(admin_view_url)
