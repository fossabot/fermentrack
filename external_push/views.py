from django.shortcuts import render
from django.contrib import messages
from django.shortcuts import redirect
from constance import config
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, RedirectView, View, FormView, DeleteView
from django.forms.forms import BaseForm  # for form_valid() typing
from django.http.request import HttpRequest  # for post() typing
from django.http.response import HttpResponse  # for form_valid() typing
from django.urls import reverse_lazy, reverse

from typing import Any, Dict

from .models import GenericPushTarget, BrewersFriendPushTarget, BrewfatherPushTarget, ThingSpeakPushTarget, GrainfatherPushTarget
from app.view_classes import ModelCreateView, ModelUpdateView, ModelFormView, ModelActionRedirectView

import fermentrack_django.settings as settings

from app.decorators import site_is_configured, gravity_support_enabled

import os, subprocess, datetime, pytz, json, logging

import external_push.forms as forms

logger = logging.getLogger(__name__)


class ExternalPushListView(LoginRequiredMixin, ListView):
    template_name = "external_push/push_target_list.html"
    context_object_name = "all_push_targets"  # for GenericPushTargets
    model = GenericPushTarget

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context.update({
            'brewers_friend_push_targets': BrewersFriendPushTarget.objects.all(),
            'brewfather_push_targets': BrewfatherPushTarget.objects.all(),
            'thingspeak_push_targets': ThingSpeakPushTarget.objects.all(),
            'grainfather_push_targets': GrainfatherPushTarget.objects.all(),
        })
        return context


# GenericPushTarget Views
class GenericPushTargetDetailView(LoginRequiredMixin, DetailView):
    model = GenericPushTarget


class GenericPushTargetCreateView(LoginRequiredMixin, ModelCreateView):
    model = GenericPushTarget
    fields = ['name', 'push_frequency', 'api_key', 'brewpi_push_selection', 'brewpi_to_push',
              'gravity_push_selection', 'gravity_sensors_to_push', 'target_host']

    def form_valid(self, form):
        target = form.instance
        messages.success(self.request, f"'Successfully added push target'")

        # Update last triggered to force a refresh in the next cycle
        target.last_triggered = target.last_triggered - datetime.timedelta(seconds=target.push_frequency)
        target.save()

        return super().form_valid(form)


class GenericPushTargetUpdateView(LoginRequiredMixin, ModelUpdateView):
    model = GenericPushTarget
    fields = ['name', 'push_frequency', 'api_key', 'brewpi_push_selection', 'brewpi_to_push',
              'gravity_push_selection', 'gravity_sensors_to_push', 'target_host']
    action = "Update"


class GenericPushTargetDeleteView(LoginRequiredMixin, DeleteView):
    model = GenericPushTarget
    success_url = reverse_lazy('push:external_push_list')

    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        messages.success(self.request, f"Successfully deleted {self.get_object().name}")  # noqa: name is valid here
        return super().post(request, *args, **kwargs)




@login_required
@site_is_configured
def external_push_brewers_friend_target_add(request):
    # TODO - Add user permissioning
    # if not request.user.has_perm('app.add_device'):
    #     messages.error(request, 'Your account is not permissioned to add devices. Please contact an admin')
    #     return redirect("/")

    form = forms.BrewersFriendPushTargetModelForm()

    if request.POST:
        form = forms.BrewersFriendPushTargetModelForm(request.POST)
        if form.is_valid():
            new_push_target = form.save()
            messages.success(request, 'Successfully added push target')

            # Update last triggered to force a refresh in the next cycle
            new_push_target.last_triggered = new_push_target.last_triggered - datetime.timedelta(seconds=new_push_target.push_frequency)
            new_push_target.save()

            return redirect('push:external_push_list')

        messages.error(request, 'Unable to add new push target')

    # Basically, if we don't get redirected, in every case we're just outputting the same template
    return render(request, template_name='external_push/brewers_friend_push_target_add.html', context={'form': form})


@login_required
@site_is_configured
def external_push_brewers_friend_view(request, push_target_id):
    # TODO - Add user permissioning
    # if not request.user.has_perm('app.add_device'):
    #     messages.error(request, 'Your account is not permissioned to add devices. Please contact an admin')
    #     return redirect("/")

    try:
        push_target = BrewersFriendPushTarget.objects.get(id=push_target_id)
    except ObjectDoesNotExist:
        messages.error(request, "Brewers's Friend push target {} does not exist".format(push_target_id))
        return redirect('push:external_push_list')

    if request.POST:
        form = forms.BrewersFriendPushTargetModelForm(request.POST, instance=push_target)
        if form.is_valid():
            updated_push_target = form.save()
            messages.success(request, 'Updated push target')
            return redirect('push:external_push_list')

        messages.error(request, 'Unable to update push target')

    form = forms.BrewersFriendPushTargetModelForm(instance=push_target)

    return render(request, template_name='external_push/brewers_friend_push_target_view.html',
                  context={'push_target': push_target, 'form': form})


@login_required
@site_is_configured
def external_push_brewers_friend_delete(request, push_target_id):
    # TODO - Add user permissioning
    # if not request.user.has_perm('app.add_device'):
    #     messages.error(request, 'Your account is not permissioned to add devices. Please contact an admin')
    #     return redirect("/")

    try:
        push_target = BrewersFriendPushTarget.objects.get(id=push_target_id)
    except ObjectDoesNotExist:
        messages.error(request, "Brewers's Friend push target {} does not exist".format(push_target_id))
        return redirect('push:external_push_list')

    message = "Brewers's Friend push target {} has been deleted".format(push_target_id)
    push_target.delete()
    messages.success(request, message)

    return redirect('push:external_push_list')


@login_required
@site_is_configured
def external_push_brewfather_target_add(request):
    # TODO - Add user permissioning
    # if not request.user.has_perm('app.add_device'):
    #     messages.error(request, 'Your account is not permissioned to add devices. Please contact an admin')
    #     return redirect("/")

    form = forms.BrewfatherPushTargetModelForm()

    if request.POST:
        form = forms.BrewfatherPushTargetModelForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['device_type'] == "gravity":
                if form.cleaned_data['gravity_sensor_to_push'] == None:
                    messages.error(request, "Brewfather push target is missing a sensor name.")
                    return redirect('push:external_push_list')
            else:
                if form.cleaned_data['brewpi_to_push'] == None:
                    messages.error(request, "Brewfather push target is missing a device name.")
                    return redirect('push:external_push_list')

            new_push_target = form.save()
            messages.success(request, 'Successfully added push target')

            # Update last triggered to force a refresh in the next cycle
            new_push_target.last_triggered = new_push_target.last_triggered - datetime.timedelta(seconds=new_push_target.push_frequency)
            new_push_target.save()

            return redirect('push:external_push_list')

        messages.error(request, 'Unable to add new push target')

    # Basically, if we don't get redirected, in every case we're just outputting the same template
    return render(request, template_name='external_push/brewfather_push_target_add.html', context={'form': form})


@login_required
@site_is_configured
def external_push_brewfather_view(request, push_target_id):
    # TODO - Add user permissioning
    # if not request.user.has_perm('app.add_device'):
    #     messages.error(request, 'Your account is not permissioned to add devices. Please contact an admin')
    #     return redirect("/")

    try:
        push_target = BrewfatherPushTarget.objects.get(id=push_target_id)
    except ObjectDoesNotExist:
        messages.error(request, "Brewfather push target {} does not exist".format(push_target_id))
        return redirect('push:external_push_list')

    if request.POST:
        form = forms.BrewfatherPushTargetModelForm(request.POST, instance=push_target)
        if form.is_valid():
            if form.cleaned_data['device_type'] == "gravity":
                if form.cleaned_data['gravity_sensor_to_push'] == None:
                    messages.error(request, "Brewfather push target {} is missing a sensor name.".format(push_target_id))
                    return redirect('push:external_push_list')
            else:
                if form.cleaned_data['brewpi_to_push'] == None:
                    messages.error(request, "Brewfather push target {} is missing a device name.".format(push_target_id))
                    return redirect('push:external_push_list')

            updated_push_target = form.save()
            messages.success(request, 'Updated push target')
            return redirect('push:external_push_list')

        messages.error(request, 'Unable to update push target')

    form = forms.BrewfatherPushTargetModelForm(instance=push_target)

    return render(request, template_name='external_push/brewfather_push_target_view.html',
                  context={'push_target': push_target, 'form': form})


@login_required
@site_is_configured
def external_push_brewfather_delete(request, push_target_id):
    # TODO - Add user permissioning
    # if not request.user.has_perm('app.add_device'):
    #     messages.error(request, 'Your account is not permissioned to add devices. Please contact an admin')
    #     return redirect("/")

    try:
        push_target = BrewfatherPushTarget.objects.get(id=push_target_id)
    except ObjectDoesNotExist:
        messages.error(request, "Brewfather push target {} does not exist".format(push_target_id))
        return redirect('push:external_push_list')

    message = "Brewfather push target {} has been deleted".format(push_target_id)
    push_target.delete()
    messages.success(request, message)

    return redirect('push:external_push_list')




@login_required
@site_is_configured
def external_push_thingspeak_target_add(request):
    # TODO - Add user permissioning
    # if not request.user.has_perm('app.add_device'):
    #     messages.error(request, 'Your account is not permissioned to add devices. Please contact an admin')
    #     return redirect("/")

    form = forms.ThingSpeakPushTargetModelForm()

    if request.POST:
        form = forms.ThingSpeakPushTargetModelForm(request.POST)
        if form.is_valid():
            new_push_target = form.save()
            messages.success(request, 'Successfully added push target')

            # Update last triggered to force a refresh in the next cycle
            new_push_target.last_triggered = new_push_target.last_triggered - datetime.timedelta(seconds=new_push_target.push_frequency)
            new_push_target.save()

            return redirect('push:external_push_list')

        messages.error(request, 'Unable to add new push target')

    # Basically, if we don't get redirected, in every case we're just outputting the same template
    return render(request, template_name='external_push/thingspeak_push_target_add.html', context={'form': form})

@login_required
@site_is_configured
def external_push_thingspeak_view(request, push_target_id):
    # TODO - Add user permissioning
    # if not request.user.has_perm('app.add_device'):
    #     messages.error(request, 'Your account is not permissioned to add devices. Please contact an admin')
    #     return redirect("/")

    try:
        push_target = ThingSpeakPushTarget.objects.get(id=push_target_id)
    except ObjectDoesNotExist:
        messages.error(request, "ThingSpeak push target {} does not exist".format(push_target_id))
        return redirect('push:external_push_list')

    if request.POST:
        form = forms.ThingSpeakPushTargetModelForm(request.POST, instance=push_target)
        if form.is_valid():
            updated_push_target = form.save()
            messages.success(request, 'Updated push target')
            return redirect('push:external_push_list')

        messages.error(request, 'Unable to update push target')

    form = forms.ThingSpeakPushTargetModelForm(instance=push_target)

    return render(request, template_name='external_push/thingspeak_push_target_view.html',
                  context={'push_target': push_target, 'form': form})

@login_required
@site_is_configured
def external_push_thingspeak_delete(request, push_target_id):
    # TODO - Add user permissioning
    # if not request.user.has_perm('app.add_device'):
    #     messages.error(request, 'Your account is not permissioned to add devices. Please contact an admin')
    #     return redirect("/")

    try:
        push_target = ThingSpeakPushTarget.objects.get(id=push_target_id)
    except ObjectDoesNotExist:
        messages.error(request, "ThingSpeak push target {} does not exist".format(push_target_id))
        return redirect('push:external_push_list')

    message = "ThingSpeak push target {} has been deleted".format(push_target_id)
    push_target.delete()
    messages.success(request, message)

    return redirect('push:external_push_list')


@login_required
@site_is_configured
def external_push_grainfather_target_add(request):
    # TODO - Add user permissioning
    # if not request.user.has_perm('app.add_device'):
    #     messages.error(request, 'Your account is not permissioned to add devices. Please contact an admin')
    #     return redirect("/")

    form = forms.GrainfatherPushTargetModelForm()

    if request.POST:
        form = forms.GrainfatherPushTargetModelForm(request.POST)
        if form.is_valid():
            new_push_target = form.save()
            messages.success(request, 'Successfully added push target')

            # Update last triggered to force a refresh in the next cycle
            new_push_target.last_triggered = new_push_target.last_triggered - datetime.timedelta(seconds=new_push_target.push_frequency)
            new_push_target.save()

            return redirect('push:external_push_list')

        messages.error(request, 'Unable to add new push target')

    # Basically, if we don't get redirected, in every case we're just outputting the same template
    return render(request, template_name='external_push/grainfather_push_target_add.html', context={'form': form})


@login_required
@site_is_configured
def external_push_grainfather_view(request, push_target_id):
    # TODO - Add user permissioning
    # if not request.user.has_perm('app.add_device'):
    #     messages.error(request, 'Your account is not permissioned to add devices. Please contact an admin')
    #     return redirect("/")

    try:
        push_target = GrainfatherPushTarget.objects.get(id=push_target_id)
    except ObjectDoesNotExist:
        messages.error(request, "Grainfather push target {} does not exist".format(push_target_id))
        return redirect('push:external_push_list')

    if request.POST:
        form = forms.GrainfatherPushTargetModelForm(request.POST, instance=push_target)
        if form.is_valid():
            updated_push_target = form.save()
            messages.success(request, 'Updated push target')
            return redirect('push:external_push_list')

        messages.error(request, 'Unable to update push target')

    form = forms.GrainfatherPushTargetModelForm(instance=push_target)

    return render(request, template_name='external_push/grainfather_push_target_view.html',
                  context={'push_target': push_target, 'form': form})


@login_required
@site_is_configured
def external_push_grainfather_delete(request, push_target_id):
    # TODO - Add user permissioning
    # if not request.user.has_perm('app.add_device'):
    #     messages.error(request, 'Your account is not permissioned to add devices. Please contact an admin')
    #     return redirect("/")

    try:
        push_target = GrainfatherPushTarget.objects.get(id=push_target_id)
    except ObjectDoesNotExist:
        messages.error(request, "Grainfather push target {} does not exist".format(push_target_id))
        return redirect('push:external_push_list')

    message = "Grainfather push target {} has been deleted".format(push_target_id)
    push_target.delete()
    messages.success(request, message)

    return redirect('push:external_push_list')



