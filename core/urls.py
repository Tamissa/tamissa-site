# Import URL path helper
from django.urls import path

# Import views from this app
from . import views


urlpatterns = [
    # Home page
    path("", views.home, name="home"),
]