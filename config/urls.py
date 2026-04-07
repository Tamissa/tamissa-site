from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/',  admin.site.urls),
    path('',        include('gallery.urls', namespace='gallery')),

    # ── shop app has been removed from routing ──
    # If you want to fully remove it later, delete the shop/ directory
    # and remove 'shop' from INSTALLED_APPS in settings.py
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
