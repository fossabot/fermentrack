import pytest
from pytest_django.asserts import assertContains, assertNotContains   # noqa: this does actually exist
from decimal import Decimal, getcontext

from django.urls import reverse


from .factories import UserFactory, GenericPushTargetFactory
from .factories import user, genericpushtarget  # noqa: fixtures must be imported
from ..models import GenericPushTarget

from ..views import ExternalPushListView

pytestmark = pytest.mark.django_db


# ExternalPushListView Tests
def test_good_externalpushlistview(client, user):
    client.force_login(user)  # Make the client authenticate
    url = reverse("push:external_push_list")  # Specify the URL of the view
    response = client.get(url)  # Use the client to make the request
    assert response.status_code == 200  # Test that the response is valid
    assertContains(response, 'External Push Targets')  # Test that the response contains the page header


def test_good_externalpushlistview_contains_3_genericpushtargets(client, user):
    # Create three objects to test with
    obj1 = GenericPushTargetFactory()
    obj2 = GenericPushTargetFactory()
    obj3 = GenericPushTargetFactory()

    client.force_login(user)  # Make the client authenticate
    url = reverse("push:external_push_list")  # Specify the URL of the view
    response = client.get(url)  # Use the client to make the request

    assertContains(response, obj1.name)
    assertContains(response, obj2.name)
    assertContains(response, obj3.name)
