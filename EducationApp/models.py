from django.db import models
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
import datetime

# تعریف توابع validator
phone_validator = RegexValidator(
    regex=r'^\+?1?\d{10,15}$',
    message='شماره تلفن باید بین 10 تا 15 رقم باشد و با فرمت صحیح وارد شود.'
)

national_id_validator = RegexValidator(
    regex=r'^\d{10}$',
    message='کد ملی باید دقیقاً 10 رقم باشد.'
)

# مدل پایه برای اطلاعات مشترک افراد
class Person(models.Model):
    """
    مدل پایه برای ذخیره اطلاعات مشترک افراد (دانشجو، استاد، کارمند)
    """
    first_name = models.CharField(max_length=50, verbose_name='نام', help_text='نام فرد')
    last_name = models.CharField(max_length=50, verbose_name='نام خانوادگی', help_text='نام خانوادگی فرد')
    national_id = models.CharField(
        max_length=10,
        unique=True,
        validators=[national_id_validator],
        verbose_name='کد ملی',
        help_text='کد ملی 10 رقمی فرد'
    )
    birth_date = models.CharField(
        max_length=10,
        verbose_name='تاریخ تولد (شمسی)',
        help_text='تاریخ تولد به فرمت YYYY/MM/DD (شمسی)',
        validators=[RegexValidator(regex=r'^\d{4}/\d{2}/\d{2}$', message='فرمت تاریخ شمسی باید YYYY/MM/DD باشد.')]
    )
    birth_place = models.CharField(max_length=100, verbose_name='محل تولد', help_text='شهر یا محل تولد فرد')
    father_name = models.CharField(max_length=50, verbose_name='نام پدر', help_text='نام پدر فرد')
    id_number = models.CharField(max_length=20, verbose_name='شماره شناسنامه', help_text='شماره شناسنامه فرد')

    class Gender(models.TextChoices):
        MALE = 'M', 'مرد'
        FEMALE = 'F', 'زن'

    gender = models.CharField(max_length=1, choices=Gender.choices, verbose_name='جنسیت', help_text='جنسیت فرد')
    
    class MaritalStatus(models.TextChoices):
        SINGLE = 'S', 'مجرد'
        MARRIED = 'M', 'متاهل'
    
    marital_status = models.CharField(
        max_length=1,
        choices=MaritalStatus.choices,
        verbose_name='وضعیت تاهل',
        help_text='وضعیت تاهل فرد'
    )
    address = models.TextField(verbose_name='آدرس', help_text='آدرس محل سکونت فرد')

    @property
    def full_name(self):
        """نام کامل فرد"""
        return f"{self.first_name} {self.last_name}"

    @property
    def age(self):
        """محاسبه سن تقریبی بر اساس سال تولد شمسی"""
        current_year = 1404  # فرض برای سال 1404
        birth_year = int(self.birth_date.split('/')[0])
        return current_year - birth_year

    class Meta:
        abstract = True
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return self.full_name

# مدل اطلاعات تماس
class ContactInfo(models.Model):
    """
    مدل برای ذخیره شماره‌های تماس و ایمیل‌های افراد
    """
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, verbose_name='نوع مدل')
    object_id = models.PositiveIntegerField(verbose_name='شناسه شیء')
    person = GenericForeignKey('content_type', 'object_id')
    
    class ContactType(models.TextChoices):
        MOBILE = 'M', 'موبایل'
        HOME = 'H', 'تلفن ثابت'
        EMAIL = 'E', 'ایمیل'
    
    contact_type = models.CharField(
        max_length=1,
        choices=ContactType.choices,
        verbose_name='نوع تماس',
        help_text='نوع اطلاعات تماس (موبایل، تلفن ثابت، ایمیل)'
    )
    value = models.CharField(
        max_length=100,
        verbose_name='مقدار',
        help_text='مقدار شماره تماس یا ایمیل'
    )

    def clean(self):
        if self.contact_type == self.ContactType.EMAIL:
            if '@' not in self.value or '.' not in self.value:
                raise ValidationError('ایمیل نامعتبر است.')
        else:
            phone_validator(self.value)

    class Meta:
        verbose_name = 'اطلاعات تماس'
        verbose_name_plural = 'اطلاعات تماس'
        unique_together = ['content_type', 'object_id', 'contact_type', 'value']

    def __str__(self):
        return f"{self.person.full_name if self.person else 'Unknown'} - {self.get_contact_type_display()}: {self.value}"

# مدل دانشکده
class Faculty(models.Model):
    """
    مدل برای ذخیره اطلاعات دانشکده‌ها
    """
    name = models.CharField(max_length=100, unique=True, verbose_name='نام دانشکده', help_text='نام دانشکده')
    code = models.CharField(max_length=10, unique=True, verbose_name='کد دانشکده', help_text='کد یکتای دانشکده')

    class Meta:
        verbose_name = 'دانشکده'
        verbose_name_plural = 'دانشکده‌ها'
        ordering = ['name']

    def __str__(self):
        return self.name

# مدل رشته تحصیلی
class Major(models.Model):
    """
    مدل برای ذخیره اطلاعات رشته‌های تحصیلی
    """
    name = models.CharField(max_length=100, verbose_name='نام رشته', help_text='نام رشته تحصیلی')
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='majors', verbose_name='دانشکده')
    code = models.CharField(max_length=10, unique=True, verbose_name='کد رشته', help_text='کد یکتای رشته')

    class Meta:
        verbose_name = 'رشته تحصیلی'
        verbose_name_plural = 'رشته‌های تحصیلی'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.faculty.name})"

# مدل دانشجو
class Student(Person):
    """
    مدل برای ذخیره اطلاعات دانشجویان
    """
    student_id = models.CharField(max_length=10, unique=True, verbose_name='شماره دانشجویی', help_text='شماره دانشجویی')
    major = models.ForeignKey(Major, on_delete=models.PROTECT, related_name='students', verbose_name='رشته')
    entry_year = models.CharField(
        max_length=4,
        verbose_name='سال ورود (شمسی)',
        help_text='سال ورود به دانشگاه (شمسی)',
        validators=[RegexValidator(regex=r'^\d{4}$', message='سال ورود باید 4 رقم باشد.')]
    )
    
    class MilitaryStatus(models.TextChoices):
        EXEMPT = 'E', 'معاف'
        SERVED = 'S', 'خدمت کرده'
        PENDING = 'P', 'در انتظار'
    
    military_status = models.CharField(
        max_length=1,
        choices=MilitaryStatus.choices,
        verbose_name='وضعیت نظام وظیفه',
        help_text='وضعیت نظام وظیفه (برای دانشجویان مرد)',
        blank=True
    )

    @property
    def total_credits_passed(self):
        """تعداد واحدهای گذرانده‌شده"""
        enrollments = self.enrollments.filter(grade__gte=10)
        return sum(enrollment.course.credits for enrollment in enrollments)

    @property
    def total_credits_remaining(self):
        """تعداد واحدهای باقیمانده (فرض: 140 واحد برای فارغ‌التحصیلی)"""
        return 140 - self.total_credits_passed

    @property
    def gpa(self):
        """محاسبه معدل کل"""
        enrollments = self.enrollments.filter(grade__isnull=False)
        if not enrollments:
            return 0
        total_credits = sum(enrollment.course.credits for enrollment in enrollments)
        if total_credits == 0:
            return 0
        total_grade = sum(enrollment.grade * enrollment.course.credits for enrollment in enrollments)
        return round(total_grade / total_credits, 2)

    class Meta:
        verbose_name = 'دانشجو'
        verbose_name_plural = 'دانشجویان'

# مدل استاد
class Professor(Person):
    """
    مدل برای ذخیره اطلاعات اساتید
    """
    professor_id = models.CharField(max_length=10, unique=True, verbose_name='کد استادی', help_text='کد یکتای استاد')
    faculty = models.ForeignKey(Faculty, on_delete=models.PROTECT, related_name='professors', verbose_name='دانشکده')
    
    class ContractType(models.TextChoices):
        FULL_TIME = 'F', 'تمام‌وقت'
        PART_TIME = 'P', 'پاره‌وقت'
    
    contract_type = models.CharField(
        max_length=1,
        choices=ContractType.choices,
        verbose_name='نوع قرارداد',
        help_text='نوع قرارداد استاد'
    )

    @property
    def courses_taught(self):
        """تعداد درس‌های تدریس‌شده در ترم جاری"""
        current_term = Term.objects.filter(is_current=True).first()
        if not current_term:
            return 0
        return self.course_assignments.filter(course__term=current_term).count()

    class Meta:
        verbose_name = 'استاد'
        verbose_name_plural = 'اساتید'

# مدل درس
class Course(models.Model):
    """
    مدل برای ذخیره اطلاعات دروس
    """
    name = models.CharField(max_length=100, verbose_name='نام درس', help_text='نام درس')
    code = models.CharField(max_length=10, unique=True, verbose_name='کد درس', help_text='کد یکتای درس')
    credits = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(4)],
        verbose_name='تعداد واحد',
        help_text='تعداد واحد درس (1 تا 4)'
    )
    major = models.ForeignKey(Major, on_delete=models.PROTECT, related_name='courses', verbose_name='رشته')
    term = models.ForeignKey('Term', on_delete=models.PROTECT, related_name='courses', verbose_name='ترم')

    class Meta:
        verbose_name = 'درس'
        verbose_name_plural = 'دروس'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"

# مدل ترم
class Term(models.Model):
    """
    مدل برای ذخیره اطلاعات ترم‌ها
    """
    year = models.CharField(
        max_length=4,
        verbose_name='سال (شمسی)',
        help_text='سال ترم (شمسی)',
        validators=[RegexValidator(regex=r'^\d{4}$', message='سال باید 4 رقم باشد.')]
    )
    
    class Season(models.TextChoices):
        FALL = 'F', 'پاییز'
        SPRING = 'S', 'بهار'
    
    season = models.CharField(max_length=1, choices=Season.choices, verbose_name='فصل', help_text='فصل ترم')
    is_current = models.BooleanField(default=False, verbose_name='ترم جاری', help_text='آیا این ترم جاری است؟')

    class Meta:
        verbose_name = 'ترم'
        verbose_name_plural = 'ترم‌ها'
        unique_together = ['year', 'season']
        ordering = ['-year', 'season']

    def __str__(self):
        return f"{self.get_season_display()} {self.year}"

# مدل اتاق
class Room(models.Model):
    """
    مدل برای ذخیره اطلاعات اتاق‌ها
    """
    name = models.CharField(max_length=50, verbose_name='نام اتاق', help_text='نام یا کد اتاق')
    building = models.CharField(max_length=100, verbose_name='ساختمان', help_text='نام ساختمان')
    capacity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='ظرفیت',
        help_text='ظرفیت اتاق'
    )

    class Meta:
        verbose_name = 'اتاق'
        verbose_name_plural = 'اتاق‌ها'
        ordering = ['building', 'name']

    def __str__(self):
        return f"{self.name} ({self.building})"

# مدل کلاس
class Class(models.Model):
    """
    مدل برای ذخیره اطلاعات کلاس‌ها
    """
    course = models.ForeignKey(Course, on_delete=models.PROTECT, related_name='classes', verbose_name='درس')
    room = models.ForeignKey(Room, on_delete=models.PROTECT, related_name='classes', verbose_name='اتاق')
    start_time = models.TimeField(verbose_name='زمان شروع', help_text='زمان شروع کلاس')
    end_time = models.TimeField(verbose_name='زمان پایان', help_text='زمان پایان کلاس')
    day_of_week = models.CharField(max_length=10, verbose_name='روز هفته', help_text='روز برگزاری کلاس')
    
    def clean(self):
        # بررسی تداخل زمانی
        overlapping_classes = Class.objects.filter(
            room=self.room,
            day_of_week=self.day_of_week,
            start_time__lt=self.end_time,
            end_time__gt=self.start_time
        ).exclude(pk=self.pk)
        if overlapping_classes.exists():
            raise ValidationError('تداخل زمانی با کلاس دیگر در این اتاق وجود دارد.')

    @property
    def enrolled_students(self):
        """تعداد دانشجویان ثبت‌نام‌شده"""
        return self.enrollments.count()

    class Meta:
        verbose_name = 'کلاس'
        verbose_name_plural = 'کلاس‌ها'

    def __str__(self):
        return f"{self.course.name} - {self.day_of_week} {self.start_time}"

# جدول میانی برای ثبت‌نام دانشجو
class Enrollment(models.Model):
    """
    مدل میانی برای ثبت‌نام دانشجویان در کلاس‌ها
    """
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='enrollments', verbose_name='دانشجو')
    class_instance = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='enrollments', verbose_name='کلاس')
    grade = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(20)],
        verbose_name='نمره',
        help_text='نمره دانشجو (0 تا 20)'
    )
    
    class Status(models.TextChoices):
        REGISTERED = 'R', 'ثبت‌نام‌شده'
        PASSED = 'P', 'پاس‌شده'
        FAILED = 'F', 'مردود'
    
    status = models.CharField(
        max_length=1,
        choices=Status.choices,
        default=Status.REGISTERED,
        verbose_name='وضعیت',
        help_text='وضعیت ثبت‌نام'
    )

    class Meta:
        verbose_name = 'ثبت‌نام'
        verbose_name_plural = 'ثبت‌نام‌ها'
        unique_together = ['student', 'class_instance']

    def __str__(self):
        return f"{self.student.full_name} - {self.class_instance.course.name}"

# جدول میانی برای تخصیص استاد به کلاس
class CourseAssignment(models.Model):
    """
    مدل میانی برای تخصیص اساتید به کلاس‌ها
    """
    professor = models.ForeignKey(Professor, on_delete=models.CASCADE, related_name='course_assignments', verbose_name='استاد')
    class_instance = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='course_assignments', verbose_name='کلاس')

    class Meta:
        verbose_name = 'تخصیص درس'
        verbose_name_plural = 'تخصیص دروس'
        unique_together = ['professor', 'class_instance']

    def __str__(self):
        return f"{self.professor.full_name} - {self.class_instance.course.name}"