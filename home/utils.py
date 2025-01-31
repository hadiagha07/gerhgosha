
from django.core.management.base import BaseCommand
from django.utils import timezone
from .models import Question


class Command(BaseCommand):
    help = 'غیرفعال کردن سوالات منقضی و فعال کردن سوال بعدی'

    def handle(self, *args, **options):
        now = timezone.now()

        # غیرفعال کردن سوالات منقضی شده
        Question.objects.filter(is_active=True, expiry_date__lte=now).update(is_active=False)

        # فعال کردن سوال بعدی اگر سوال فعالی وجود نداشته باشد
        if not Question.objects.filter(is_active=True).exists():
            next_question = Question.objects.filter(expiry_date__gt=now).order_by('expiry_date').first()
            if next_question:
                next_question.is_active = True
                next_question.save()