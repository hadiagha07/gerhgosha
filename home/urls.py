from django.urls import include, path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from .views import *

app_name = 'api'

schema_view = get_schema_view(
    openapi.Info(
        title="API Documentation",
        default_version='v1',
        description="API description",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('send-otp/', RequestOTPView.as_view(), name='send_otp'),  # ارسال کد تأیید
    path('verify-otp/', VerifyOTPView.as_view(), name='verify_otp'),  # تأیید کد
    path('sign-up/', SignUpView.as_view(), name='sign_up'),  # ثبت‌نام کاربر
    path('login/', LoginView.as_view(), name='login'),
    path('active-question/', ActiveQuestionView.as_view(), name='active-question'),
    path('submit-response/', SubmitResponseView.as_view(), name='submit-response'),
    path('correct-responders/', CorrectRespondersView.as_view(), name='correct-responders'),
]
