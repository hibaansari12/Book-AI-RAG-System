"""URL routing for scraper."""

from django.urls import path
from .views import ScrapeView, BulkScrapeView

urlpatterns = [
    path('scrape/', ScrapeView.as_view(), name='scrape'),
    path('bulk-scrape/', BulkScrapeView.as_view(), name='bulk-scrape'),
]
