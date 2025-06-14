# Generated by Django 5.2 on 2025-05-04 20:58

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='نام درس', max_length=100, verbose_name='نام درس')),
                ('code', models.CharField(help_text='کد یکتای درس', max_length=10, unique=True, verbose_name='کد درس')),
                ('credits', models.PositiveIntegerField(help_text='تعداد واحد درس (1 تا 4)', validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(4)], verbose_name='تعداد واحد')),
            ],
            options={
                'verbose_name': 'درس',
                'verbose_name_plural': 'دروس',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Faculty',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='نام دانشکده', max_length=100, unique=True, verbose_name='نام دانشکده')),
                ('code', models.CharField(help_text='کد یکتای دانشکده', max_length=10, unique=True, verbose_name='کد دانشکده')),
            ],
            options={
                'verbose_name': 'دانشکده',
                'verbose_name_plural': 'دانشکده\u200cها',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='نام یا کد اتاق', max_length=50, verbose_name='نام اتاق')),
                ('building', models.CharField(help_text='نام ساختمان', max_length=100, verbose_name='ساختمان')),
                ('capacity', models.PositiveIntegerField(help_text='ظرفیت اتاق', validators=[django.core.validators.MinValueValidator(1)], verbose_name='ظرفیت')),
            ],
            options={
                'verbose_name': 'اتاق',
                'verbose_name_plural': 'اتاق\u200cها',
                'ordering': ['building', 'name'],
            },
        ),
        migrations.CreateModel(
            name='Class',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.TimeField(help_text='زمان شروع کلاس', verbose_name='زمان شروع')),
                ('end_time', models.TimeField(help_text='زمان پایان کلاس', verbose_name='زمان پایان')),
                ('day_of_week', models.CharField(help_text='روز برگزاری کلاس', max_length=10, verbose_name='روز هفته')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='classes', to='EducationApp.course', verbose_name='درس')),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='classes', to='EducationApp.room', verbose_name='اتاق')),
            ],
            options={
                'verbose_name': 'کلاس',
                'verbose_name_plural': 'کلاس\u200cها',
            },
        ),
        migrations.CreateModel(
            name='Major',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='نام رشته تحصیلی', max_length=100, verbose_name='نام رشته')),
                ('code', models.CharField(help_text='کد یکتای رشته', max_length=10, unique=True, verbose_name='کد رشته')),
                ('faculty', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='majors', to='EducationApp.faculty', verbose_name='دانشکده')),
            ],
            options={
                'verbose_name': 'رشته تحصیلی',
                'verbose_name_plural': 'رشته\u200cهای تحصیلی',
                'ordering': ['name'],
            },
        ),
        migrations.AddField(
            model_name='course',
            name='major',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='courses', to='EducationApp.major', verbose_name='رشته'),
        ),
        migrations.CreateModel(
            name='Professor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(help_text='نام فرد', max_length=50, verbose_name='نام')),
                ('last_name', models.CharField(help_text='نام خانوادگی فرد', max_length=50, verbose_name='نام خانوادگی')),
                ('national_id', models.CharField(help_text='کد ملی 10 رقمی فرد', max_length=10, unique=True, validators=[django.core.validators.RegexValidator(message='کد ملی باید دقیقاً 10 رقم باشد.', regex='^\\d{10}$')], verbose_name='کد ملی')),
                ('birth_date', models.CharField(help_text='تاریخ تولد به فرمت YYYY/MM/DD (شمسی)', max_length=10, validators=[django.core.validators.RegexValidator(message='فرمت تاریخ شمسی باید YYYY/MM/DD باشد.', regex='^\\d{4}/\\d{2}/\\d{2}$')], verbose_name='تاریخ تولد (شمسی)')),
                ('birth_place', models.CharField(help_text='شهر یا محل تولد فرد', max_length=100, verbose_name='محل تولد')),
                ('father_name', models.CharField(help_text='نام پدر فرد', max_length=50, verbose_name='نام پدر')),
                ('id_number', models.CharField(help_text='شماره شناسنامه فرد', max_length=20, verbose_name='شماره شناسنامه')),
                ('gender', models.CharField(choices=[('M', 'مرد'), ('F', 'زن')], help_text='جنسیت فرد', max_length=1, verbose_name='جنسیت')),
                ('marital_status', models.CharField(choices=[('S', 'مجرد'), ('M', 'متاهل')], help_text='وضعیت تاهل فرد', max_length=1, verbose_name='وضعیت تاهل')),
                ('address', models.TextField(help_text='آدرس محل سکونت فرد', verbose_name='آدرس')),
                ('professor_id', models.CharField(help_text='کد یکتای استاد', max_length=10, unique=True, verbose_name='کد استادی')),
                ('contract_type', models.CharField(choices=[('F', 'تمام\u200cوقت'), ('P', 'پاره\u200cوقت')], help_text='نوع قرارداد استاد', max_length=1, verbose_name='نوع قرارداد')),
                ('faculty', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='professors', to='EducationApp.faculty', verbose_name='دانشکده')),
            ],
            options={
                'verbose_name': 'استاد',
                'verbose_name_plural': 'اساتید',
            },
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(help_text='نام فرد', max_length=50, verbose_name='نام')),
                ('last_name', models.CharField(help_text='نام خانوادگی فرد', max_length=50, verbose_name='نام خانوادگی')),
                ('national_id', models.CharField(help_text='کد ملی 10 رقمی فرد', max_length=10, unique=True, validators=[django.core.validators.RegexValidator(message='کد ملی باید دقیقاً 10 رقم باشد.', regex='^\\d{10}$')], verbose_name='کد ملی')),
                ('birth_date', models.CharField(help_text='تاریخ تولد به فرمت YYYY/MM/DD (شمسی)', max_length=10, validators=[django.core.validators.RegexValidator(message='فرمت تاریخ شمسی باید YYYY/MM/DD باشد.', regex='^\\d{4}/\\d{2}/\\d{2}$')], verbose_name='تاریخ تولد (شمسی)')),
                ('birth_place', models.CharField(help_text='شهر یا محل تولد فرد', max_length=100, verbose_name='محل تولد')),
                ('father_name', models.CharField(help_text='نام پدر فرد', max_length=50, verbose_name='نام پدر')),
                ('id_number', models.CharField(help_text='شماره شناسنامه فرد', max_length=20, verbose_name='شماره شناسنامه')),
                ('gender', models.CharField(choices=[('M', 'مرد'), ('F', 'زن')], help_text='جنسیت فرد', max_length=1, verbose_name='جنسیت')),
                ('marital_status', models.CharField(choices=[('S', 'مجرد'), ('M', 'متاهل')], help_text='وضعیت تاهل فرد', max_length=1, verbose_name='وضعیت تاهل')),
                ('address', models.TextField(help_text='آدرس محل سکونت فرد', verbose_name='آدرس')),
                ('student_id', models.CharField(help_text='شماره دانشجویی', max_length=10, unique=True, verbose_name='شماره دانشجویی')),
                ('entry_year', models.CharField(help_text='سال ورود به دانشگاه (شمسی)', max_length=4, validators=[django.core.validators.RegexValidator(message='سال ورود باید 4 رقم باشد.', regex='^\\d{4}$')], verbose_name='سال ورود (شمسی)')),
                ('military_status', models.CharField(blank=True, choices=[('E', 'معاف'), ('S', 'خدمت کرده'), ('P', 'در انتظار')], help_text='وضعیت نظام وظیفه (برای دانشجویان مرد)', max_length=1, verbose_name='وضعیت نظام وظیفه')),
                ('major', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='students', to='EducationApp.major', verbose_name='رشته')),
            ],
            options={
                'verbose_name': 'دانشجو',
                'verbose_name_plural': 'دانشجویان',
            },
        ),
        migrations.CreateModel(
            name='Term',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.CharField(help_text='سال ترم (شمسی)', max_length=4, validators=[django.core.validators.RegexValidator(message='سال باید 4 رقم باشد.', regex='^\\d{4}$')], verbose_name='سال (شمسی)')),
                ('season', models.CharField(choices=[('F', 'پاییز'), ('S', 'بهار')], help_text='فصل ترم', max_length=1, verbose_name='فصل')),
                ('is_current', models.BooleanField(default=False, help_text='آیا این ترم جاری است؟', verbose_name='ترم جاری')),
            ],
            options={
                'verbose_name': 'ترم',
                'verbose_name_plural': 'ترم\u200cها',
                'ordering': ['-year', 'season'],
                'unique_together': {('year', 'season')},
            },
        ),
        migrations.AddField(
            model_name='course',
            name='term',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='courses', to='EducationApp.term', verbose_name='ترم'),
        ),
        migrations.CreateModel(
            name='ContactInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.PositiveIntegerField(verbose_name='شناسه شیء')),
                ('contact_type', models.CharField(choices=[('M', 'موبایل'), ('H', 'تلفن ثابت'), ('E', 'ایمیل')], help_text='نوع اطلاعات تماس (موبایل، تلفن ثابت، ایمیل)', max_length=1, verbose_name='نوع تماس')),
                ('value', models.CharField(help_text='مقدار شماره تماس یا ایمیل', max_length=100, verbose_name='مقدار')),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype', verbose_name='نوع مدل')),
            ],
            options={
                'verbose_name': 'اطلاعات تماس',
                'verbose_name_plural': 'اطلاعات تماس',
                'unique_together': {('content_type', 'object_id', 'contact_type', 'value')},
            },
        ),
        migrations.CreateModel(
            name='CourseAssignment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('class_instance', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='course_assignments', to='EducationApp.class', verbose_name='کلاس')),
                ('professor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='course_assignments', to='EducationApp.professor', verbose_name='استاد')),
            ],
            options={
                'verbose_name': 'تخصیص درس',
                'verbose_name_plural': 'تخصیص دروس',
                'unique_together': {('professor', 'class_instance')},
            },
        ),
        migrations.CreateModel(
            name='Enrollment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('grade', models.FloatField(blank=True, help_text='نمره دانشجو (0 تا 20)', null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(20)], verbose_name='نمره')),
                ('status', models.CharField(choices=[('R', 'ثبت\u200cنام\u200cشده'), ('P', 'پاس\u200cشده'), ('F', 'مردود')], default='R', help_text='وضعیت ثبت\u200cنام', max_length=1, verbose_name='وضعیت')),
                ('class_instance', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='enrollments', to='EducationApp.class', verbose_name='کلاس')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='enrollments', to='EducationApp.student', verbose_name='دانشجو')),
            ],
            options={
                'verbose_name': 'ثبت\u200cنام',
                'verbose_name_plural': 'ثبت\u200cنام\u200cها',
                'unique_together': {('student', 'class_instance')},
            },
        ),
    ]
