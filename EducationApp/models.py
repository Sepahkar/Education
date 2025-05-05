from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from jalali_date import datetime2jalali, date2jalali
from django.utils import timezone
import jdatetime

# انواع جنسیت
GENDER_CHOICES = [
    ('M', 'مرد'),
    ('F', 'زن'),
]

# وضعیت تاهل
MARITAL_STATUS_CHOICES = [
    ('S', 'مجرد'),
    ('M', 'متاهل'),
    ('D', 'مطلقه'),
    ('W', 'بیوه'),
]

# وضعیت نظام وظیفه
MILITARY_STATUS_CHOICES = [
    ('S', 'در حال خدمت'),
    ('E', 'معاف'),
    ('F', 'به پایان رسیده'),
    ('P', 'معافیت تحصیلی'),
    ('N', 'مشمول'),
]

# نوع شماره تماس
CONTACT_TYPE_CHOICES = [
    ('M', 'موبایل'),
    ('H', 'منزل'),
    ('W', 'محل کار'),
    ('O', 'سایر'),
]

# نوع قرارداد استاد
PROFESSOR_CONTRACT_CHOICES = [
    ('FT', 'تمام وقت'),
    ('PT', 'پاره وقت'),
    ('I', 'حق التدریس'),
]

# وضعیت دانشجویی
STUDENT_STATUS_CHOICES = [
    ('AC', 'فعال'),
    ('ON', 'مرخصی'),
    ('GR', 'فارغ التحصیل'),
    ('EX', 'اخراج'),
    ('WT', 'انصراف'),
]

# وضعیت ثبت نام
ENROLLMENT_STATUS_CHOICES = [
    ('P', 'در انتظار تایید'),
    ('A', 'تایید شده'),
    ('R', 'رد شده'),
    ('D', 'حذف شده'),
]

# نیمسال تحصیلی
SEMESTER_TYPE_CHOICES = [
    ('F', 'پاییز'),
    ('S', 'بهار'),
]

# روزهای هفته
WEEKDAY_CHOICES = [
    (0, 'شنبه'),
    (1, 'یکشنبه'),
    (2, 'دوشنبه'),
    (3, 'سه شنبه'),
    (4, 'چهارشنبه'),
    (5, 'پنجشنبه'),
    (6, 'جمعه'),
]

# اعتبارسنجی کد ملی
def validate_national_code(value):
    if len(value) != 10:
        raise models.ValidationError('کد ملی باید ۱۰ رقم باشد')
    
    check = int(value[9])
    total = sum(int(value[i]) * (10 - i) for i in range(9)) % 11
    
    if (total < 2 and check == total) or (total >= 2 and check + total == 11):
        return value
    raise models.ValidationError('کد ملی نامعتبر است')


# مدل شخص (مدل پایه انتزاعی)
class Person(models.Model):
    """
    مدل پایه برای تمام افراد شامل اطلاعات مشترک فردی مانند نام، نام خانوادگی، کد ملی و غیره
    """
    first_name = models.CharField(max_length=100, verbose_name=_('نام'))
    last_name = models.CharField(max_length=100, verbose_name=_('نام خانوادگی'))
    national_code = models.CharField(
        max_length=10, 
        unique=True,
        validators=[validate_national_code],
        verbose_name=_('کد ملی')
    )
    birth_certificate_number = models.CharField(max_length=10, blank=True, null=True, verbose_name=_('شماره شناسنامه'))
    birth_date = models.DateField(blank=True, null=True, verbose_name=_('تاریخ تولد'))
    birth_place = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('محل تولد'))
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, verbose_name=_('جنسیت'))
    marital_status = models.CharField(
        max_length=1, 
        choices=MARITAL_STATUS_CHOICES, 
        blank=True, 
        null=True, 
        verbose_name=_('وضعیت تاهل')
    )
    address = models.TextField(blank=True, null=True, verbose_name=_('آدرس'))
    photo = models.ImageField(upload_to='person_photos/', blank=True, null=True, verbose_name=_('عکس'))

    class Meta:
        abstract = True
        verbose_name = _('شخص')
        verbose_name_plural = _('اشخاص')

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def jalali_birth_date(self):
        if self.birth_date:
            return date2jalali(self.birth_date).strftime('%Y/%m/%d')
        return None

    @property
    def age(self):
        if self.birth_date:
            today = timezone.now().date()
            return (today - self.birth_date).days // 365
        return None


# اطلاعات تماس
class ContactInfo(models.Model):
    """
    اطلاعات تماس برای افراد مختلف. هر شخص می‌تواند چندین راه ارتباطی داشته باشد.
    """
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, verbose_name=_('نوع شخص'))
    object_id = models.PositiveIntegerField(verbose_name=_('شناسه شخص'))
    content_object = GenericForeignKey('content_type', 'object_id')
    
    contact_type = models.CharField(max_length=1, choices=CONTACT_TYPE_CHOICES, verbose_name=_('نوع تماس'))
    value = models.CharField(max_length=100, verbose_name=_('مقدار'))
    is_primary = models.BooleanField(default=False, verbose_name=_('اصلی'))
    
    class Meta:
        verbose_name = _('اطلاعات تماس')
        verbose_name_plural = _('اطلاعات تماس')
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
        ]
    
    def __str__(self):
        return f"{self.get_contact_type_display()}: {self.value}"


# دانشکده
class Faculty(models.Model):
    """
    دانشکده‌های موجود در دانشگاه
    """
    code = models.CharField(max_length=10, unique=True, verbose_name=_('کد دانشکده'))
    name = models.CharField(max_length=100, verbose_name=_('نام دانشکده'))
    establishment_date = models.DateField(blank=True, null=True, verbose_name=_('تاریخ تاسیس'))
    address = models.TextField(blank=True, null=True, verbose_name=_('آدرس'))
    description = models.TextField(blank=True, null=True, verbose_name=_('توضیحات'))
    
    class Meta:
        verbose_name = _('دانشکده')
        verbose_name_plural = _('دانشکده‌ها')
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    @property
    def jalali_establishment_date(self):
        if self.establishment_date:
            return date2jalali(self.establishment_date).strftime('%Y/%m/%d')
        return None


# رشته تحصیلی
class Department(models.Model):
    """
    رشته‌های تحصیلی موجود در دانشکده‌ها
    """
    code = models.CharField(max_length=10, unique=True, verbose_name=_('کد رشته'))
    name = models.CharField(max_length=100, verbose_name=_('نام رشته'))
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, verbose_name=_('دانشکده'))
    establishment_date = models.DateField(blank=True, null=True, verbose_name=_('تاریخ تاسیس'))
    total_credits = models.PositiveIntegerField(default=0, verbose_name=_('تعداد کل واحدها'))
    description = models.TextField(blank=True, null=True, verbose_name=_('توضیحات'))
    
    class Meta:
        verbose_name = _('رشته تحصیلی')
        verbose_name_plural = _('رشته‌های تحصیلی')
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.faculty.name})"
    
    @property
    def jalali_establishment_date(self):
        if self.establishment_date:
            return date2jalali(self.establishment_date).strftime('%Y/%m/%d')
        return None


# استاد
class Professor(Person):
    """
    اطلاعات مربوط به اساتید دانشگاه
    """
    professor_code = models.CharField(max_length=10, unique=True, verbose_name=_('کد استادی'))
    department = models.ForeignKey(Department, on_delete=models.CASCADE, verbose_name=_('رشته تحصیلی'))
    academic_rank = models.CharField(max_length=50, blank=True, null=True, verbose_name=_('مرتبه علمی'))
    contract_type = models.CharField(
        max_length=2, 
        choices=PROFESSOR_CONTRACT_CHOICES, 
        verbose_name=_('نوع قرارداد')
    )
    employment_date = models.DateField(verbose_name=_('تاریخ استخدام'))
    education_level = models.CharField(max_length=50, verbose_name=_('مدرک تحصیلی'))
    specialization = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('تخصص'))
    
    class Meta:
        verbose_name = _('استاد')
        verbose_name_plural = _('اساتید')
    
    def __str__(self):
        return f"{self.academic_rank} {self.first_name} {self.last_name}"
    
    @property
    def teaching_years(self):
        if self.employment_date:
            today = timezone.now().date()
            return (today - self.employment_date).days // 365
        return 0
    
    @property
    def jalali_employment_date(self):
        return date2jalali(self.employment_date).strftime('%Y/%m/%d')


# دانشجو
class Student(Person):
    """
    اطلاعات مربوط به دانشجویان دانشگاه
    """
    student_code = models.CharField(max_length=10, unique=True, verbose_name=_('شماره دانشجویی'))
    department = models.ForeignKey(Department, on_delete=models.CASCADE, verbose_name=_('رشته تحصیلی'))
    admission_date = models.DateField(verbose_name=_('تاریخ پذیرش'))
    military_status = models.CharField(
        max_length=1, 
        choices=MILITARY_STATUS_CHOICES, 
        blank=True, 
        null=True, 
        verbose_name=_('وضعیت نظام وظیفه')
    )
    student_status = models.CharField(
        max_length=2, 
        choices=STUDENT_STATUS_CHOICES, 
        default='AC', 
        verbose_name=_('وضعیت دانشجویی')
    )
    graduation_date = models.DateField(blank=True, null=True, verbose_name=_('تاریخ فارغ‌التحصیلی'))
    
    class Meta:
        verbose_name = _('دانشجو')
        verbose_name_plural = _('دانشجویان')
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.student_code})"
    
    @property
    def jalali_admission_date(self):
        return date2jalali(self.admission_date).strftime('%Y/%m/%d')
    
    @property
    def jalali_graduation_date(self):
        if self.graduation_date:
            return date2jalali(self.graduation_date).strftime('%Y/%m/%d')
        return None
    
    @property
    def is_graduated(self):
        return self.student_status == 'GR' and self.graduation_date is not None
    
    @property
    def study_years(self):
        end_date = self.graduation_date if self.graduation_date else timezone.now().date()
        return (end_date - self.admission_date).days // 365


# ترم تحصیلی
class Semester(models.Model):
    """
    ترم‌های تحصیلی دانشگاه
    """
    academic_year = models.PositiveIntegerField(verbose_name=_('سال تحصیلی'))
    semester_type = models.CharField(max_length=1, choices=SEMESTER_TYPE_CHOICES, verbose_name=_('نیمسال'))
    start_date = models.DateField(verbose_name=_('تاریخ شروع'))
    end_date = models.DateField(verbose_name=_('تاریخ پایان'))
    is_active = models.BooleanField(default=False, verbose_name=_('ترم فعال'))
    
    class Meta:
        verbose_name = _('ترم تحصیلی')
        verbose_name_plural = _('ترم‌های تحصیلی')
        ordering = ['-academic_year', '-semester_type']
        constraints = [
            models.UniqueConstraint(fields=['academic_year', 'semester_type'], name='unique_semester')
        ]
    
    def __str__(self):
        semester_name = 'پاییز' if self.semester_type == 'F' else 'بهار'
        return f"{semester_name} {self.academic_year}"
    
    @property
    def jalali_start_date(self):
        return date2jalali(self.start_date).strftime('%Y/%m/%d')
    
    @property
    def jalali_end_date(self):
        return date2jalali(self.end_date).strftime('%Y/%m/%d')
    
    @property
    def is_current(self):
        today = timezone.now().date()
        return self.start_date <= today <= self.end_date


# اتاق
class Room(models.Model):
    """
    اتاق‌های دانشگاه برای برگزاری کلاس‌ها
    """
    room_number = models.CharField(max_length=20, verbose_name=_('شماره اتاق'))
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, verbose_name=_('دانشکده'))
    capacity = models.PositiveIntegerField(verbose_name=_('ظرفیت'))
    has_projector = models.BooleanField(default=False, verbose_name=_('دارای ویدیو پروژکتور'))
    floor = models.PositiveIntegerField(verbose_name=_('طبقه'))
    description = models.TextField(blank=True, null=True, verbose_name=_('توضیحات'))
    
    class Meta:
        verbose_name = _('اتاق')
        verbose_name_plural = _('اتاق‌ها')
        ordering = ['faculty__name', 'room_number']
        constraints = [
            models.UniqueConstraint(fields=['room_number', 'faculty'], name='unique_room_number_per_faculty')
        ]
    
    def __str__(self):
        return f"{self.room_number} - {self.faculty.name}"


# درس
class Course(models.Model):
    """
    دروس ارائه شده در دانشگاه
    """
    course_code = models.CharField(max_length=10, unique=True, verbose_name=_('کد درس'))
    title = models.CharField(max_length=100, verbose_name=_('عنوان درس'))
    department = models.ForeignKey(Department, on_delete=models.CASCADE, verbose_name=_('رشته تحصیلی'))
    credits = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(6)], verbose_name=_('تعداد واحد'))
    is_practical = models.BooleanField(default=False, verbose_name=_('عملی'))
    prerequisites = models.ManyToManyField('self', symmetrical=False, blank=True, verbose_name=_('پیش‌نیازها'))
    description = models.TextField(blank=True, null=True, verbose_name=_('توضیحات'))
    
    class Meta:
        verbose_name = _('درس')
        verbose_name_plural = _('دروس')
        ordering = ['department__name', 'title']
    
    def __str__(self):
        return f"{self.title} ({self.course_code})"


# کلاس (ارائه دروس)
class ClassOffering(models.Model):
    """
    کلاس‌های ارائه شده در هر ترم
    """
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name=_('درس'))
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, verbose_name=_('ترم'))
    professor = models.ForeignKey(Professor, on_delete=models.CASCADE, verbose_name=_('استاد'))
    class_code = models.CharField(max_length=20, verbose_name=_('کد کلاس'))
    capacity = models.PositiveIntegerField(verbose_name=_('ظرفیت'))
    
    class Meta:
        verbose_name = _('کلاس')
        verbose_name_plural = _('کلاس‌ها')
        ordering = ['semester', 'course__title']
        constraints = [
            models.UniqueConstraint(fields=['course', 'semester', 'class_code'], name='unique_class_offering')
        ]
    
    def __str__(self):
        return f"{self.course.title} - {self.class_code} - {self.semester}"
    
    @property
    def enrolled_count(self):
        return self.enrollment_set.filter(status__in=['A', 'P']).count()
    
    @property
    def remaining_capacity(self):
        return self.capacity - self.enrolled_count


# جلسات کلاس
class ClassSession(models.Model):
    """
    جلسات کلاس و برنامه زمانی
    """
    class_offering = models.ForeignKey(ClassOffering, on_delete=models.CASCADE, verbose_name=_('کلاس'))
    room = models.ForeignKey(Room, on_delete=models.CASCADE, verbose_name=_('اتاق'))
    weekday = models.PositiveSmallIntegerField(choices=WEEKDAY_CHOICES, verbose_name=_('روز هفته'))
    start_time = models.TimeField(verbose_name=_('ساعت شروع'))
    end_time = models.TimeField(verbose_name=_('ساعت پایان'))
    
    class Meta:
        verbose_name = _('جلسه کلاس')
        verbose_name_plural = _('جلسات کلاس')
        ordering = ['class_offering', 'weekday', 'start_time']
        constraints = [
            models.CheckConstraint(check=models.Q(start_time__lt=models.F('end_time')), name='check_session_times'),
        ]
    
    def __str__(self):
        weekday_name = dict(WEEKDAY_CHOICES)[self.weekday]
        return f"{self.class_offering} - {weekday_name} از {self.start_time} تا {self.end_time}"
    
    def save(self, *args, **kwargs):
        # بررسی تداخل زمانی با دیگر جلسات در همان اتاق
        overlapping_sessions = ClassSession.objects.filter(
            room=self.room,
            weekday=self.weekday,
            start_time__lt=self.end_time,
            end_time__gt=self.start_time
        )
        
        if self.pk:  # اگر جلسه فعلی قبلاً ذخیره شده است
            overlapping_sessions = overlapping_sessions.exclude(pk=self.pk)
        
        if overlapping_sessions.exists():
            raise models.ValidationError('تداخل زمانی با جلسه دیگری در این اتاق وجود دارد')
        
        super().save(*args, **kwargs)


# ثبت نام دانشجو در کلاس
class Enrollment(models.Model):
    """
    ثبت نام دانشجویان در کلاس‌ها
    """
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name=_('دانشجو'))
    class_offering = models.ForeignKey(ClassOffering, on_delete=models.CASCADE, verbose_name=_('کلاس'))
    enrollment_date = models.DateTimeField(auto_now_add=True, verbose_name=_('تاریخ ثبت‌نام'))
    status = models.CharField(max_length=1, choices=ENROLLMENT_STATUS_CHOICES, default='P', verbose_name=_('وضعیت'))
    grade = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        blank=True, 
        null=True, 
        validators=[MinValueValidator(0), MaxValueValidator(20)], 
        verbose_name=_('نمره')
    )
    
    class Meta:
        verbose_name = _('ثبت‌نام')
        verbose_name_plural = _('ثبت‌نام‌ها')
        constraints = [
            models.UniqueConstraint(fields=['student', 'class_offering'], name='unique_enrollment')
        ]
    
    def __str__(self):
        return f"{self.student} - {self.class_offering}"
    
    @property
    def has_passed(self):
        return self.grade is not None and self.grade >= 10
    
    @property
    def jalali_enrollment_date(self):
        return datetime2jalali(self.enrollment_date).strftime('%Y/%m/%d %H:%M:%S')
    
    def clean(self):
        # بررسی ظرفیت کلاس
        if self.status in ['A', 'P']:
            enrolled_count = Enrollment.objects.filter(
                class_offering=self.class_offering, 
                status__in=['A', 'P']
            ).count()
            
            if self.pk:  # اگر ثبت نام فعلی قبلاً ذخیره شده است
                enrolled_count -= 1
            
            if enrolled_count >= self.class_offering.capacity:
                raise models.ValidationError('ظرفیت کلاس تکمیل شده است')
        
        # بررسی تداخل زمانی با کلاس‌های دیگر
        if self.status in ['A', 'P']:
            current_sessions = ClassSession.objects.filter(class_offering=self.class_offering)
            other_enrollments = Enrollment.objects.filter(
                student=self.student, 
                status__in=['A', 'P'], 
                class_offering__semester=self.class_offering.semester
            )
            
            if self.pk:  # اگر ثبت نام فعلی قبلاً ذخیره شده است
                other_enrollments = other_enrollments.exclude(pk=self.pk)
            
            for enrollment in other_enrollments:
                other_sessions = ClassSession.objects.filter(class_offering=enrollment.class_offering)
                
                for current_session in current_sessions:
                    for other_session in other_sessions:
                        if (
                            current_session.weekday == other_session.weekday and
                            current_session.start_time < other_session.end_time and
                            current_session.end_time > other_session.start_time
                        ):
                            raise models.ValidationError('تداخل زمانی با کلاس دیگری وجود دارد')
