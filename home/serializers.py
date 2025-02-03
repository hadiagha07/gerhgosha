from rest_framework import serializers
from .models import *


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = [
            'phone_number',
            'first_name',
            'last_name',
            'province',
            'gender',
            'password',
            'confirm_password'
        ]
        extra_kwargs = {
            'phone_number': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
            'province': {'required': True},
            'gender': {'required': True},
        }

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"password": "گذرواژه و تأیید گذرواژه یکسان نیستند."})
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        password = validated_data.pop('password')


        phone_number = validated_data.pop('phone_number')


        user = User.objects.create_user(
            phone_number=phone_number,
            password=password,
            **validated_data
        )
        return user


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['id', 'text']


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
