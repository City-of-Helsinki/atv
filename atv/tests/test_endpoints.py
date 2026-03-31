import pytest


def test_healthz_endpoint(client):
    response = client.get("/healthz")
    assert response.status_code == 200


@pytest.mark.django_db
def test_readiness_endpoint(client):
    response = client.get("/readiness")
    assert response.status_code == 200
