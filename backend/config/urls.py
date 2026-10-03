"""
config/urls.py — URLs principales del proyecto Damasco Gift Cards.
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.views.static import serve

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('giftcards.urls')),
    # Fondos de tarjeta y logos de empresas. Se sirven también con DEBUG=false
    # porque el portal no tiene otro servidor de archivos delante.
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]
