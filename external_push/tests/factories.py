from typing import Any, Sequence

from django.contrib.auth import get_user_model
from factory import Faker, post_generation
from factory.django import DjangoModelFactory

import pytest
from pytz import UTC

import factory.fuzzy

from ..models import GenericPushTarget
import datetime

# External Fixtures
@pytest.fixture
def user():
    return UserFactory()


# Fixtures
@pytest.fixture
def genericpushtarget():
    return GenericPushTargetFactory()


class UserFactory(DjangoModelFactory):
    username = Faker("user_name")
    email = Faker("email")
    first_name = Faker("name")

    @post_generation
    def password(self, create: bool, extracted: Sequence[Any], **kwargs):
        password = (
            extracted
            if extracted
            else Faker(
                "password",
                length=42,
                special_chars=True,
                digits=True,
                upper_case=True,
                lower_case=True,
            ).evaluate(None, None, extra={"locale": None})
        )
        self.set_password(password)

    class Meta:
        model = get_user_model()
        django_get_or_create = ["username"]


class GenericPushTargetFactory(factory.django.DjangoModelFactory):
    name = factory.fuzzy.FuzzyText()
    status = factory.fuzzy.FuzzyChoice([x[0] for x in GenericPushTarget.STATUS_CHOICES])
    push_frequency = factory.fuzzy.FuzzyChoice([x[0] for x in GenericPushTarget.PUSH_FREQUENCY_CHOICES])
    api_key = factory.fuzzy.FuzzyText()
    brewpi_push_selection = factory.fuzzy.FuzzyChoice([x[0] for x in GenericPushTarget.SENSOR_SELECT_CHOICES])

    # TODO - Fix this
    # brewpi_to_push = models.ManyToManyField(to=BrewPiDevice, related_name="push_targets", blank=True, default=None,
    #                                         help_text="BrewPi Devices to push (ignored if 'all' devices selected)")

    gravity_push_selection = factory.fuzzy.FuzzyChoice([x[0] for x in GenericPushTarget.SENSOR_SELECT_CHOICES])

    # TODO - Fix this
    # gravity_sensors_to_push = factory.SubFactory(TapFactory)
    # gravity_sensors_to_push = models.ManyToManyField(to=GravitySensor, related_name="push_targets", blank=True, default=None,
    #                                                  help_text="Gravity Sensors to push (ignored if 'all' "
    #                                                            "sensors selected)")

    target_type = factory.fuzzy.FuzzyChoice([x[0] for x in GenericPushTarget.SENSOR_PUSH_CHOICES])
    target_host = factory.fuzzy.FuzzyText()
    target_port = factory.fuzzy.FuzzyInteger(low=10, high=65535)

    data_format = factory.fuzzy.FuzzyChoice([x[0] for x in GenericPushTarget.DATA_FORMAT_CHOICES])
    error_text = factory.fuzzy.FuzzyText()

    last_triggered = factory.fuzzy.FuzzyDateTime(start_dt=datetime.datetime(2008, 1, 1, tzinfo=UTC))

    class Meta:
        model = GenericPushTarget
