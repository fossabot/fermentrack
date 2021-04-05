from django.urls import path

from . import views

app_name = "external_push"

urlpatterns = [
    ## External Push Views
    path(route='', view=views.external_push_list, name='external_push_list'),
    path(route='add/', view=views.external_push_generic_target_add, name='external_push_generic_target_add'),
    path(route='view/<int:push_target_id>/', view=views.external_push_view, name='external_push_view'),
    path(route='delete/<int:push_target_id>/', view=views.external_push_delete, name='external_push_delete'),

    path(route='brewersfriend/add/', view=views.external_push_brewers_friend_target_add, name='external_push_brewers_friend_target_add'),
    path(route='brewersfriend/view/<int:push_target_id>/', view=views.external_push_brewers_friend_view, name='external_push_brewers_friend_view'),
    path(route='brewersfriend/delete/<int:push_target_id>/', view=views.external_push_brewers_friend_delete, name='external_push_brewers_friend_delete'),

    path(route='brewfather/add/', view=views.external_push_brewfather_target_add, name='external_push_brewfather_target_add'),
    path(route='brewfather/view/<int:push_target_id>/', view=views.external_push_brewfather_view, name='external_push_brewfather_view'),
    path(route='brewfather/delete/<int:push_target_id>/', view=views.external_push_brewfather_delete, name='external_push_brewfather_delete'),

    path(route='thingspeak/add/', view=views.external_push_thingspeak_target_add, name='external_push_thingspeak_target_add'),
    path(route='thingspeak/view/<int:push_target_id>/', view=views.external_push_thingspeak_view, name='external_push_thingspeak_view'),
    path(route='thingspeak/delete/<int:push_target_id>/', view=views.external_push_thingspeak_delete, name='external_push_thingspeak_delete'),

    path(route='grainfather/add/', view=views.external_push_grainfather_target_add, name='external_push_grainfather_target_add'),
    path(route='grainfather/view/<int:push_target_id>/', view=views.external_push_grainfather_view, name='external_push_grainfather_view'),
    path(route='grainfather/delete/<int:push_target_id>/', view=views.external_push_grainfather_delete, name='external_push_grainfather_delete'),
]
