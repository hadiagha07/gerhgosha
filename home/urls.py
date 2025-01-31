from django.urls import path
from .views import *

app_name = 'api'


urlpatterns = [
    path('active-question/', ActiveQuestionView.as_view(), name='active-question'),
]