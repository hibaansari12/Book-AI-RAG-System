"""URL routing for books app."""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BookViewSet, BulkBookUploadView, ChatHistoryView

router = DefaultRouter()
router.register(r'', BookViewSet, basename='book')

urlpatterns = [
    path('bulk/', BulkBookUploadView.as_view(), name='bulk-upload'),
    path('chat-history/', ChatHistoryView.as_view(), name='chat-history'),
    path('', include(router.urls)),
]
