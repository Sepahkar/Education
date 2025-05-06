from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from django.db.models import Avg, Count
from . import models

# اینلاین برای اطلاعات تماس
class ContactInfoInline(GenericTabularInline):
    model = models.ContactInfo
    extra = 1

# اینلاین ثبت‌نام دانشجو
class EnrollmentInline(admin.TabularInline):
    model = models.Enrollment
    extra = 0
    fields = ('class_offering', 'status', 'grade', 'has_passed')
    readonly_fields = ('has_passed',)
    
    def has_passed(self, obj):
        return "✅ قبول" if obj.has_passed else "❌ مردود" if obj.grade is not None else "⏳ در حال تحصیل"
    has_passed.short_description = 'وضعیت'

# اینلاین کلاس‌های تدریس‌شده توسط استاد
class ProfessorClassesInline(admin.TabularInline):
    model = models.ClassOffering
    extra = 0
    fields = ('class_code', 'course', 'semester', 'enrolled_students', 'average_grade')
    readonly_fields = ('enrolled_students', 'average_grade')
    
    def enrolled_students(self, obj):
        return obj.enrollment_set.count()
    enrolled_students.short_description = 'تعداد دانشجویان'
    
    def average_grade(self, obj):
        avg = obj.enrollment_set.filter(grade__isnull=False).aggregate(avg=Avg('grade'))['avg']
        return round(avg, 2) if avg is not None else '-'
    average_grade.short_description = 'میانگین نمرات'

# اینلاین دروس رشته تحصیلی
class DepartmentCoursesInline(admin.TabularInline):
    model = models.Course
    extra = 0
    fields = ('course_code', 'title', 'credits', 'is_practical')

# اینلاین دانشجویان رشته تحصیلی
class DepartmentStudentsInline(admin.TabularInline):
    model = models.Student
    extra = 0
    fields = ('student_code', 'first_name', 'last_name', 'student_status')

# اینلاین کلاس‌های درس
class CourseClassesInline(admin.TabularInline):
    model = models.ClassOffering
    extra = 0
    fields = ('class_code', 'semester', 'professor', 'capacity', 'enrolled_count')
    readonly_fields = ('enrolled_count',)

# اینلاین جلسات کلاس
class ClassSessionInline(admin.TabularInline):
    model = models.ClassSession
    extra = 1

# ادمین دانشکده
@admin.register(models.Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'establishment_date')
    search_fields = ('name', 'code')

# ادمین رشته تحصیلی
@admin.register(models.Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'faculty', 'total_credits', 'student_count')
    list_filter = ('faculty',)
    search_fields = ('name', 'code')
    inlines = [DepartmentCoursesInline, DepartmentStudentsInline]
    
    def student_count(self, obj):
        return obj.student_set.count()
    student_count.short_description = 'تعداد دانشجویان'

# ادمین استاد
@admin.register(models.Professor)
class ProfessorAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'professor_code', 'department', 'academic_rank', 'contract_type')
    list_filter = ('department', 'academic_rank', 'contract_type')
    search_fields = ('first_name', 'last_name', 'professor_code', 'national_code')
    inlines = [ContactInfoInline, ProfessorClassesInline]
    fieldsets = (
        ('اطلاعات شخصی', {
            'fields': ('first_name', 'last_name', 'national_code', 'birth_certificate_number', 
                      'birth_date', 'birth_place', 'gender', 'marital_status', 'address', 'photo')
        }),
        ('اطلاعات دانشگاهی', {
            'fields': ('professor_code', 'department', 'academic_rank', 'contract_type', 
                      'employment_date', 'education_level', 'specialization')
        }),
    )

# ادمین دانشجو
@admin.register(models.Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'student_code', 'department', 'student_status', 'admission_date')
    list_filter = ('department', 'student_status', 'gender')
    search_fields = ('first_name', 'last_name', 'student_code', 'national_code')
    inlines = [ContactInfoInline, EnrollmentInline]
    fieldsets = (
        ('اطلاعات شخصی', {
            'fields': ('first_name', 'last_name', 'national_code', 'birth_certificate_number', 
                      'birth_date', 'birth_place', 'gender', 'marital_status', 'address', 'photo')
        }),
        ('اطلاعات دانشجویی', {
            'fields': ('student_code', 'department', 'admission_date', 'military_status', 
                      'student_status', 'graduation_date')
        }),
    )

# ادمین ترم تحصیلی
@admin.register(models.Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'academic_year', 'semester_type', 'start_date', 'end_date', 'is_active')
    list_filter = ('academic_year', 'semester_type', 'is_active')

# ادمین اتاق
@admin.register(models.Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('room_number', 'faculty', 'capacity', 'floor', 'has_projector')
    list_filter = ('faculty', 'floor', 'has_projector')
    search_fields = ('room_number',)

# ادمین درس
@admin.register(models.Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'course_code', 'department', 'credits', 'is_practical')
    list_filter = ('department', 'is_practical')
    search_fields = ('title', 'course_code')
    filter_horizontal = ('prerequisites',)
    inlines = [CourseClassesInline]

# ادمین کلاس
@admin.register(models.ClassOffering)
class ClassOfferingAdmin(admin.ModelAdmin):
    list_display = ('course', 'class_code', 'semester', 'professor', 'capacity', 'enrolled_count', 'remaining_capacity')
    list_filter = ('semester', 'course__department')
    search_fields = ('course__title', 'class_code', 'professor__last_name')
    inlines = [ClassSessionInline]

# ادمین ثبت نام
@admin.register(models.Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'class_offering', 'status', 'grade', 'has_passed')
    list_filter = ('status', 'class_offering__semester')
    search_fields = ('student__first_name', 'student__last_name', 'student__student_code')

# ثبت مدل اطلاعات تماس
@admin.register(models.ContactInfo)
class ContactInfoAdmin(admin.ModelAdmin):
    list_display = ('content_object', 'contact_type', 'value', 'is_primary')
    list_filter = ('contact_type', 'is_primary')