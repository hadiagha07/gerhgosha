from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore
from django.utils import timezone
from .models import Question

def check_expired_questions():
    """بررسی سوالات منقضی و فعال کردن سوال جدید"""
    expired_questions = Question.objects.filter(expiry_date__lte=timezone.now())
    expired_questions.delete()

    next_question = Question.objects.filter(is_active=False).order_by('expiry_date').first()
    if next_question:
        next_question.is_active = True
        next_question.save()

def start_scheduler():
    """شروع شِدولر برای بررسی سوالات"""
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), 'default')

    # ثبت وظیفه بررسی سوالات منقضی
    scheduler.add_job(
        check_expired_questions,
        'interval',
        minutes=1,
        id='check_expired',
        replace_existing=True
    )
    scheduler.start()
