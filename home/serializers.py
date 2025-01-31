from rest_framework import serializers
from .models import *

class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['id', 'text', 'votes']

class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'text', 'expiry_date', 'is_active', 'choices']


class UserResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserResponse
        fields = ['user', 'question', 'selected_choice', 'is_correct']
        read_only_fields = ['user', 'is_correct']

    def validate(self, data):
        user = self.context['request'].user
        question = data['question']
        selected_choice = data['selected_choice']

        # بررسی اینکه آیا کاربر قبلاً به این سوال پاسخ داده است
        if UserResponse.objects.filter(user=user, question=question).exists():
            raise serializers.ValidationError('شما قبلاً به این سوال پاسخ داده‌اید.')

        # بررسی اینکه آیا گزینه انتخاب شده متعلق به سوال است
        if selected_choice.question != question:
            raise serializers.ValidationError('گزینه انتخاب شده متعلق به این سوال نیست.')

        return data