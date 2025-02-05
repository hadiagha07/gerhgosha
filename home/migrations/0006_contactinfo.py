# Generated by Django 5.1.4 on 2025-02-05 15:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0005_alter_ticket_options_remove_ticket_message_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContactInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.CharField(blank=True, max_length=255, null=True, verbose_name='آدرس')),
                ('phone_number', models.CharField(blank=True, max_length=20, null=True, verbose_name='شماره تماس')),
                ('telegram_id', models.CharField(blank=True, max_length=100, null=True, verbose_name='آیدی تلگرام')),
                ('ita_id', models.CharField(blank=True, max_length=100, null=True, verbose_name='آیدی ایتا')),
                ('whatsapp_id', models.CharField(blank=True, max_length=100, null=True, verbose_name='آیدی واتساپ')),
                ('instagram_id', models.CharField(blank=True, max_length=100, null=True, verbose_name='آیدی اینستاگرام')),
            ],
            options={
                'verbose_name': 'اطلاعات تماس',
                'verbose_name_plural': 'اطلاعات تماس',
            },
        ),
    ]
