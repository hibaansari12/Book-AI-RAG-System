"""
Main URL configuration.
Routes API endpoints to respective apps.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/books/', include('books.urls')),
    path('api/ai/', include('ai_engine.urls')),
    path('api/scraper/', include('scraper.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
