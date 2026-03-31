from django.urls import path
from . import views

app_name = 'gallery'

urlpatterns = [
    path('',                        views.home,           name='home'),
    path('artwork/<slug:slug>/',    views.artwork_detail, name='artwork_detail'),
    path('contact/',                views.contact,        name='contact'),
]
