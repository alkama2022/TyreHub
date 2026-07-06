from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

def test_if_user_is_anonymous_returns_401():
    client = APIClient()

    url = reverse("category-list")
    response = client.post(url, {"title": "a"})

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


@pytest.mark.django_db
class TestProductCategory:

    def test_get_categories_returns_200(self):
        client = APIClient()

        url = reverse("category-list")

        response = client.get(url)

        assert response.status_code == status.HTTP_200_OK

    def test_anonymous_user_cannot_create_category(self):
        client = APIClient()

        url = reverse("category-list")

        response = client.post(url, {"title": "Tyres"})

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_retrieve_category(self):
        ...
        # reverse("category-detail", args=[category.id])

    def test_admin_can_create_category(self):
        ...

    def test_admin_can_update_category(self):
        ...

    def test_admin_can_delete_category(self):
        ...