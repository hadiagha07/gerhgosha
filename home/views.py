from django.contrib.auth import authenticate
from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from .models import *
from .serializers import *
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class SignUpView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="ثبت‌نام کاربر جدید و دریافت توکن",
        request_body=UserSerializer,
        responses={201: UserSerializer}
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            "user": UserSerializer(user).data,
            "token": token.key
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="ورود کاربر با شماره موبایل و رمز عبور",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'phone_number': openapi.Schema(type=openapi.TYPE_STRING, description='شماره موبایل کاربر'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='رمز عبور کاربر'),
            },
            required=['phone_number', 'password'],
        ),
        responses={200: "ورود موفق", 401: "نام کاربری یا رمز عبور اشتباه است"}
    )
    def post(self, request):
        phone_number = request.data.get('phone_number')
        password = request.data.get('password')

        if not phone_number or not password:
            return Response({'error': 'شماره موبایل و رمز عبور الزامی هستند.'}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(phone_number=phone_number, password=password)
        if user is None:
            return Response({'error': 'نام کاربری یا رمز عبور اشتباه است.'}, status=status.HTTP_401_UNAUTHORIZED)

        token, created = Token.objects.get_or_create(user=user)
        return Response({
            "user": UserSerializer(user).data,
            "token": token.key
        }, status=status.HTTP_200_OK)



class ActiveQuestionView(generics.RetrieveAPIView):
    """نمایش سوال فعال"""
    serializer_class = QuestionSerializer

    def get_object(self):
        return Question.objects.filter(is_active=True).first()


class SubmitResponseView(APIView):
    permission_classes = [IsAuthenticated]  # کاربران باید حتما احراز هویت شوند

    @swagger_auto_schema(
        operation_description="ثبت پاسخ کاربر برای سوال فعال",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'selected_choice_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='آیدی گزینه انتخاب شده'),
            },
            required=['selected_choice_id'],
        ),
        responses={
            201: openapi.Response("پاسخ ثبت شد."),
            400: openapi.Response("خطا: گزینه معتبر نیست یا سوالی فعال وجود ندارد."),
            401: openapi.Response("خطا: احراز هویت لازم است.")
        }
    )
    def post(self, request):
        if not request.user.is_authenticated:
            return Response({'error': 'احراز هویت لازم است.'}, status=status.HTTP_401_UNAUTHORIZED)

        selected_choice_id = request.data.get('selected_choice_id')

        question = Question.objects.filter(is_active=True).first()
        if not question:
            return Response({'error': 'هیچ سوال فعالی وجود ندارد.'}, status=status.HTTP_400_BAD_REQUEST)

        if UserResponse.objects.filter(user=request.user, question=question).exists():
            return Response({'error': 'شما قبلاً به این سوال پاسخ داده‌اید.'}, status=status.HTTP_400_BAD_REQUEST)

        selected_choice = Choice.objects.filter(id=selected_choice_id, question=question).first()
        if not selected_choice:
            return Response({'error': 'گزینه انتخاب شده معتبر نیست.'}, status=status.HTTP_400_BAD_REQUEST)

        user_response = UserResponse.objects.create(
            user=request.user,
            question=question,
            selected_choice=selected_choice,
            is_correct=selected_choice.is_correct
        )

        if selected_choice.is_correct:
            question.correct_responders.add(request.user)

        return Response({
            'message': 'پاسخ شما ثبت شد.',
            'is_correct': selected_choice.is_correct
        }, status=status.HTTP_201_CREATED)




class CorrectRespondersView(APIView):
    """لیست کاربران با پاسخ صحیح به سوال فعال"""
    permission_classes = [AllowAny]

    def get(self, request):
        question = Question.objects.filter(is_active=True).first()
        if not question:
            return Response({'error': 'هیچ سوال فعالی وجود ندارد.'}, status=status.HTTP_400_BAD_REQUEST)

        correct_responders = question.correct_responders.all()
        correct_responders_data = [
            {
                'phone_number': user.phone_number,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'province': user.province,
                'gender': user.get_gender_display(),
            }
            for user in correct_responders
        ]

        return Response({'correct_responders': correct_responders_data}, status=status.HTTP_200_OK)
