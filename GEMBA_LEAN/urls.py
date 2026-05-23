from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', include('salle.urls')),           # Vos URLs d'abord (AVANT l'admin)
    path('admin/', admin.site.urls),           # L'admin après
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)