from rest_framework import generics
from .models import Question
from .serializers import QuestionSerializer

class ActiveQuestionView(generics.RetrieveAPIView):
    serializer_class = QuestionSerializer

    def get_object(self):
        return Question.objects.filter(is_active=True).first()