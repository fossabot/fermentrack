import pytest
from pytest_django.asserts import assertContains, assertNotContains   # noqa: this does actually exist

from django.urls import reverse
import datetime
from django.utils import timezone

from .factories import UserFactory, GenericPushTargetFactory
from .factories import user, genericpushtarget  # noqa: fixtures must be imported
from ..models import GenericPushTarget

pytestmark = pytest.mark.django_db


# GenericPushTarget Detail Tests
def test_good_genericpushtarget_detail(client, user, genericpushtarget):
    client.force_login(user)  # Make the client authenticate
    url = reverse("push:external_push_view", kwargs={'pk': genericpushtarget.pk})
    response = client.get(url)  # Use the client to make the request
    assert response.status_code == 200  # Test that the response is valid
    assertContains(response, str(genericpushtarget))  # Test that the response contains the object


# GenericPushTarget Create Tests
def test_good_genericpushtarget_create_view(client, user):
    client.force_login(user)  # Make the client authenticate
    url = reverse("push:external_push_generic_target_add")
    response = client.get(url)
    assert response.status_code == 200


def test_good_genericpushtarget_create_form_valid(client, user):
    client.force_login(user)  # Authenticate the user
    form_data = {
        'name': "Target",
        'push_frequency': 60-1,
        'api_key': 'apikey',
        'brewpi_push_selection': GenericPushTarget.SENSOR_SELECT_NONE,
        # 'brewpi_to_push': "",  # TODO - Change this when we have a BrewPiDeviceFactory
        'gravity_push_selection': GenericPushTarget.SENSOR_SELECT_NONE,
        # 'gravity_sensors_to_push': "",  # TODO - Change this when we have a GravitySensorFactory
        'target_host': 'http://127.0.0.1/',
    }
    url = reverse("push:external_push_generic_target_add")
    response = client.post(url, form_data)

    target = GenericPushTarget.objects.get(name=form_data['name'])  # Get the object based on the name
    assert target.push_frequency == form_data['push_frequency']
    assert target.api_key == form_data['api_key']
    assert target.brewpi_push_selection == form_data['brewpi_push_selection']
    assert target.gravity_push_selection == form_data['gravity_push_selection']
    assert target.target_host == form_data['target_host']
    assert target.last_triggered <= (timezone.now() - datetime.timedelta(seconds=target.push_frequency))


# GenericPushTarget Update Test
def test_good_genericpushtarget_update_view(client, user, genericpushtarget):
    client.force_login(user)  # Authenticate the user
    url = reverse("push:genericpushtarget_update", kwargs={'pk': genericpushtarget.pk})
    response = client.get(url)
    assertContains(response, "Update Push Target")


def test_good_genericpushtarget_update(client, user, genericpushtarget):
    """POST request to GenericPushTargetUpdateView updates a GenericPushTarget and redirects"""
    client.force_login(user)
    form_data = {
        'name': "Target",
        'push_frequency': 60-1,
        'api_key': 'apikey',
        'brewpi_push_selection': GenericPushTarget.SENSOR_SELECT_NONE,
        'gravity_push_selection': GenericPushTarget.SENSOR_SELECT_NONE,
        'target_host': 'http://127.0.0.1/',
    }

    url = reverse("push:genericpushtarget_update", kwargs={'pk': genericpushtarget.pk})
    response = client.post(url, form_data)

    genericpushtarget.refresh_from_db()
    assert genericpushtarget.name == form_data['name']


# GenericPushTarget Delete Test
def test_good_genericpushtarget_delete_get(client, user, genericpushtarget):
    """Request to GenericPushTargetDeleteView generates the form to delete the object"""
    client.force_login(user)  # Authenticate the user
    url = reverse("push:genericpushtarget_delete", kwargs={"pk": genericpushtarget.pk})
    response = client.get(url)

    assertContains(response, str(genericpushtarget))


def test_good_genericpushtarget_delete_post(client, user, genericpushtarget):
    """Request to GenericPushTargetDeleteView deletes a GenericPushTarget and redirects"""
    client.force_login(user)  # Authenticate the user

    object_pk = genericpushtarget.pk

    url = reverse("push:genericpushtarget_delete", kwargs={"pk": genericpushtarget.pk})
    response = client.post(url, {'Confirm': "Confirm"})

    assert GenericPushTarget.objects.filter(pk=object_pk).count() == 0
