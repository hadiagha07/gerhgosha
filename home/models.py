from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class CustomUserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError('شماره موبایل الزامی است')
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(phone_number, password, **extra_fields)


class User(AbstractUser):
    username = None
    email = None

    phone_number = models.CharField(max_length=15, unique=True, verbose_name='شماره موبایل')
    first_name = models.CharField(max_length=30, verbose_name='نام')
    last_name = models.CharField(max_length=30, verbose_name='نام خانوادگی')
    province = models.CharField(max_length=50, verbose_name='استان')

    GENDER_CHOICES = [
        ('M', 'مرد'),
        ('F', 'زن'),
    ]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, verbose_name='جنسیت')

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'province', 'gender']

    objects = CustomUserManager()  # استفاده از مدیر سفارشی

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.phone_number}"


class Question(models.Model):
    text = models.TextField(verbose_name='متن سوال')
    expiry_date = models.DateTimeField(verbose_name='تاریخ انقضا')
    is_active = models.BooleanField(default=False, verbose_name='فعال')
    correct_responders = models.ManyToManyField(User, blank=True, related_name='correct_questions',
                                                verbose_name='کاربران با پاسخ درست')

    def __str__(self):
        return self.text[:50]

    def save(self, *args, **kwargs):
        if self.is_active:
            # غیرفعال کردن تمام سوالات دیگر هنگام فعال کردن این سوال
            Question.objects.exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=200, verbose_name='متن گزینه')
    is_correct = models.BooleanField(default=False, verbose_name='آیا پاسخ درست است؟')

    def __str__(self):
        return self.text



class UserResponse(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='کاربر')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name='سوال')
    selected_choice = models.ForeignKey(Choice, on_delete=models.CASCADE, verbose_name='گزینه انتخاب شده')
    is_correct = models.BooleanField(default=False, verbose_name='آیا پاسخ درست است؟')

    def save(self, *args, **kwargs):
        if self.selected_choice.is_correct:
            self.is_correct = True
            self.question.correct_responders.add(self.user)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.phone_number} - {self.question.text[:50]}"
