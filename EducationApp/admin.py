from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from . import models

# اینلاین برای اطلاعات تماس
class ContactInfoInline(GenericTabularInline):
    model = models.ContactInfo
    extra = 1

# ادمین دانشکده
@admin.register(models.Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'establishment_date')
    search_fields = ('name', 'code')

# ادمین رشته تحصیلی
@admin.register(models.Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'faculty', 'total_credits')
    list_filter = ('faculty',)
    search_fields = ('name', 'code')

# ادمین استاد
@admin.register(models.Professor)
class ProfessorAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'professor_code', 'department', 'academic_rank', 'contract_type')
    list_filter = ('department', 'academic_rank', 'contract_type')
    search_fields = ('first_name', 'last_name', 'professor_code', 'national_code')
    inlines = [ContactInfoInline]
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
    inlines = [ContactInfoInline]
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

# ادمین جلسات کلاس
class ClassSessionInline(admin.TabularInline):
    model = models.ClassSession
    extra = 1

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
