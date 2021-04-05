from django.views.generic import ListView, DetailView, CreateView, UpdateView, View, FormView, DeleteView
from django.http.request import HttpRequest  # for post() typing
from django.http.response import HttpResponse  # for form_valid() typing
from django.utils.translation import gettext_lazy as _
from django.views.generic import RedirectView
from django.views.generic.edit import ProcessFormView
from django.views.generic.detail import SingleObjectTemplateResponseMixin
from django.views.generic.edit import FormMixin
from django.views.generic.detail import SingleObjectMixin

from typing import Any, Dict


# Abstract Views
class ModelCreateView(CreateView):
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['model'] = self.model
        return context


class ModelUpdateView(UpdateView):
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['model'] = self.model
        return context


class ModelActionRedirectView(SingleObjectMixin, RedirectView):
    """
    Utility view for taking an action on an object and redirecting.

    By default this is a model instance looked up from `self.queryset`, but the
    view will support display of *any* object by overriding `self.get_object()`.
    """

    permanent = False

    def __init__(self, **kwargs):
        self.object = None
        super().__init__(**kwargs)

    def perform_action(self, request, *args, **kwargs):
        raise NotImplementedError("perform_action must be specified on ModelActionRedirectViews")

    def get_redirect_url(self, *args, **kwargs) -> str:
        """
        Return the URL redirect to. Attempts to redirect to self.object.get_absolute_url()
        """
        if self.object:
            url = self.object.get_absolute_url()
            return url
        else:
            url = super().get_redirect_url(*args, **kwargs)
            return url

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        # Process getting the object (similar to other views using SingleObjectMixin)
        self.object = self.get_object()

        # Call the action
        self.perform_action(request, *args, **kwargs)

        # Handle the redirect
        return super(ModelActionRedirectView, self).get(request, *args, **kwargs)


class ModelFormView(FormMixin, SingleObjectTemplateResponseMixin, SingleObjectMixin, ProcessFormView):
    """Subclassable view that can be used to process forms that are associated with objects but aren't ModelForms"""
    # model = None

    def __init__(self, **kwargs):
        self.object = None
        super().__init__(**kwargs)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)

