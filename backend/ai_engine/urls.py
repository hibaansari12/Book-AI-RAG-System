#URL routing for AI engine

from django.urls import path
from .views import (
    AskQuestionView,
    GenerateInsightsView,
    IndexBookView,
    BatchProcessView
)

urlpatterns = [
    path('ask/', AskQuestionView.as_view(), name='ask-question'),
    path('generate-insights/', GenerateInsightsView.as_view(), name='generate-insights'),
    path('index-book/', IndexBookView.as_view(), name='index-book'),
    path('batch-process/', BatchProcessView.as_view(), name='batch-process'),
]

