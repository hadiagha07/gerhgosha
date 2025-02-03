from django.urls import path
from .views import *

app_name = 'api'


urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('active-question/', ActiveQuestionView.as_view(), name='active-question'),
    path('submit-response/<int:question_id>/', SubmitResponseView.as_view(), name='submit-response'),
    path('correct-responders/<int:question_id>/', CorrectRespondersView.as_view(), name='correct-responders'),

]