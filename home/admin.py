# admin.py
from django.contrib import admin
from .models import Question, Choice

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 2

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['text', 'expiry_date', 'is_active']
    list_filter = ['is_active']
    inlines = [ChoiceInline]