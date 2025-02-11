# admin.py
from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin


class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('phone_number', 'password')}),
        ('اطلاعات شخصی', {'fields': ('first_name', 'last_name', 'province', 'gender')}),
        ('دسترسیها', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('تاریخهای مهم', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'phone_number',
                'first_name',
                'last_name',
                'province',
                'gender',
                'password1',
                'password2',
            ),
        }),
    )

    list_display = ('phone_number', 'first_name', 'last_name', 'is_staff')
    search_fields = ('phone_number', 'first_name', 'last_name')
    ordering = ('phone_number',)


admin.site.register(User, CustomUserAdmin)


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 2


class QuestionAdmin(admin.ModelAdmin):
    list_display = ('is_active', 'expiry_date')
    inlines = [ChoiceInline]

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj:  # فقط زمانی که یک سوال خاص در حال ویرایش است
            correct_users = UserResponse.objects.filter(
                question=obj, is_correct=True
            ).values_list('user', flat=True)
            form.base_fields['correct_responders'].queryset = obj.correct_responders.filter(id__in=correct_users)
        return form


admin.site.register(Question, QuestionAdmin)


@admin.register(UserResponse)
class UserResponseAdmin(admin.ModelAdmin):
    list_display = ('user', 'question_text', 'selected_choice_text', 'is_correct')
    search_fields = ('user__username', 'user__phone_number', 'question__text')
    list_filter = ('is_correct', 'question__is_active')
    ordering = ('-id',)
    readonly_fields = ('is_correct',)

    # نمایش متن سؤال و گزینه به جای آیدی‌ها
    def question_text(self, obj):
        return obj.question.text if obj.question else '-'

    question_text.short_description = 'متن سؤال'

    def selected_choice_text(self, obj):
        return obj.selected_choice.text if obj.selected_choice else '-'

    selected_choice_text.short_description = 'گزینه انتخاب شده'

    # جلوگیری از تغییر بعضی فیلدهای حساس
    def get_readonly_fields(self, request, obj=None):
        readonly = list(self.readonly_fields)
        if obj:
            readonly.extend(['user', 'question', 'selected_choice'])
        return readonly


class TicketReplyInline(admin.TabularInline):
    """
    نمایش پاسخ‌های مرتبط با هر تیکت به صورت اینلاین
    """
    model = TicketReply
    extra = 1  # تعداد خطوط خالی اضافه برای پاسخ‌های جدید
    fields = ('reply_body', 'admin', 'created_at')
    readonly_fields = ('admin', 'created_at')

    def has_delete_permission(self, request, obj=None):
        return True

    def save_model(self, request, obj, form, change):
        # تنظیم مدیر به صورت خودکار هنگام ثبت پاسخ
        if not obj.admin:
            obj.admin = request.user
        super().save_model(request, obj, form, change)


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    """
    نمایش تیکت‌ها با پاسخ‌ها به صورت اینلاین
    """
    list_display = ('subject', 'user', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at')
    search_fields = ('subject', 'user__phone_number')
    inlines = [TicketReplyInline]


@admin.register(ContactInfo)
class ContactInfoAdmin(admin.ModelAdmin):
    fieldsets = (
        ('اطلاعات تماس', {
            'fields': (
                'address',
                'phone_number',
            )
        }),
        ('شبکه‌های اجتماعی', {
            'fields': (
                'telegram_id',
                'ita_id',
                'whatsapp_id',
                'instagram_id',
            )
        }),
    )
