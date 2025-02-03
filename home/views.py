from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.authtoken.models import Token
from .models import *
from .serializers import *



class SignUpView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            "user": UserSerializer(user).data,
            "token": token.key
        }, status=status.HTTP_201_CREATED)



class ActiveQuestionView(generics.RetrieveAPIView):
    serializer_class = QuestionSerializer

    def get_object(self):
        return Question.objects.filter(is_active=True).first()


class SubmitResponseView(APIView):
    def post(self, request, question_id):
        user = request.user
        try:
            question = Question.objects.get(id=question_id)
        except Question.DoesNotExist:
            return Response({'error': 'سوال معتبر نیست.'}, status=status.HTTP_400_BAD_REQUEST)

        selected_choice_id = request.data.get('selected_choice_id')
        try:
            selected_choice = Choice.objects.get(id=selected_choice_id, question=question)
        except Choice.DoesNotExist:
            return Response({'error': 'گزینه معتبر نیست.'}, status=status.HTTP_400_BAD_REQUEST)

        # ذخیره پاسخ کاربر
        user_response = UserResponse(
            user=user,
            question=question,
            selected_choice=selected_choice
        )
        user_response.save()

        # اگر پاسخ درست بود، کاربر به لیست کاربران با پاسخ درست اضافه می‌شود
        if user_response.is_correct:
            # مثلاً می‌توانید یک لیست از کاربران با پاسخ درست در مدل Question ذخیره کنید
            question.correct_responders.add(user)

        return Response({'message': 'پاسخ شما ثبت شد.', 'is_correct': user_response.is_correct},
                        status=status.HTTP_201_CREATED)



class CorrectRespondersView(APIView):
    def get(self, request, question_id):
        try:
            question = Question.objects.get(id=question_id)
        except Question.DoesNotExist:
            return Response({'error': 'سوال معتبر نیست.'}, status=status.HTTP_400_BAD_REQUEST)

        # دریافت کاربرانی که پاسخ درست داده‌اند
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