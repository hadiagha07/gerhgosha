from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.timezone import now, timedelta
import random


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


class PhoneOTP(models.Model):
    phone_number = models.CharField(max_length=15, unique=True, verbose_name='شماره موبایل')
    otp = models.CharField(max_length=6, verbose_name='کد تأیید')
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    def generate_otp(self):
        self.otp = f"{random.randint(100000, 999999)}"
        self.created_at = now()
        self.save()


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
        # غیرفعال کردن سوالات دیگر هنگام فعال‌سازی این سوال
        if self.is_active:
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


class Ticket(models.Model):
    STATUS_CHOICES = [
        ('pending', 'در حال بررسی'),
        ('replied', 'پاسخ داده شده'),
    ]

    subject = models.CharField(max_length=255, verbose_name='موضوع')
    body = models.TextField(verbose_name='متن پیام')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='کاربر')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='وضعیت')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ آخرین به‌روزرسانی')

    class Meta:
        verbose_name = 'تیکت'
        verbose_name_plural = 'تیکت‌ها'

    def __str__(self):
        return self.subject


class TicketReply(models.Model):
    ticket = models.ForeignKey(Ticket, related_name='replies', on_delete=models.CASCADE, verbose_name='تیکت')
    reply_body = models.TextField(verbose_name='متن پاسخ')
    admin = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='مدیر')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ پاسخ')

    class Meta:
        verbose_name = 'پاسخ تیکت'
        verbose_name_plural = 'پاسخ‌های تیکت'

    def __str__(self):
        return f"پاسخ به {self.ticket.subject}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.ticket.status != 'replied':
            self.ticket.status = 'replied'
            self.ticket.save(update_fields=['status'])


class ContactInfo(models.Model):
    address = models.CharField(max_length=255, verbose_name='آدرس', blank=True, null=True)
    phone_number = models.CharField(max_length=20, verbose_name='شماره تماس', blank=True, null=True)
    telegram_id = models.CharField(max_length=100, verbose_name='آیدی تلگرام', blank=True, null=True)
    ita_id = models.CharField(max_length=100, verbose_name='آیدی ایتا', blank=True, null=True)
    whatsapp_id = models.CharField(max_length=100, verbose_name='آیدی واتساپ', blank=True, null=True)
    instagram_id = models.CharField(max_length=100, verbose_name='آیدی اینستاگرام', blank=True, null=True)

    class Meta:
        verbose_name = 'اطلاعات تماس'
        verbose_name_plural = 'اطلاعات تماس'

    def __str__(self):
        return "اطلاعات تماس"

    def save(self, *args, **kwargs):
        # جلوگیری از ایجاد بیش از یک نمونه
        if not self.pk and ContactInfo.objects.exists():
            raise ValidationError("فقط یک نمونه از اطلاعات تماس می‌تواند وجود داشته باشد")
        super().save(*args, **kwargs)