from rest_framework import serializers
from django.db.models import Avg, Sum
from .models import (
    Faculty, Department, Professor, Student, Semester, 
    Room, Course, ClassOffering, ClassSession, Enrollment, ContactInfo
)

class ContactInfoSerializer(serializers.ModelSerializer):
    """
    سریالایزر اطلاعات تماس
    """
    contact_type_display = serializers.CharField(source='get_contact_type_display', read_only=True)
    
    class Meta:
        model = ContactInfo
        fields = '__all__'
        
class FacultySerializer(serializers.ModelSerializer):
    """
    سریالایزر دانشکده
    """
    department_count = serializers.SerializerMethodField()
    jalali_establishment_date = serializers.CharField(read_only=True)
    
    class Meta:
        model = Faculty
        fields = '__all__'
        
    def get_department_count(self, obj):
        """
        محاسبه تعداد رشته‌های هر دانشکده
        """
        return obj.department_set.count()
        
class DepartmentSerializer(serializers.ModelSerializer):
    """
    سریالایزر رشته تحصیلی
    """
    faculty_name = serializers.CharField(source='faculty.name', read_only=True)
    student_count = serializers.SerializerMethodField()
    course_count = serializers.SerializerMethodField()
    jalali_establishment_date = serializers.CharField(read_only=True)
    
    class Meta:
        model = Department
        fields = '__all__'
        
    def get_student_count(self, obj):
        """
        محاسبه تعداد دانشجویان هر رشته
        """
        return obj.student_set.count()
        
    def get_course_count(self, obj):
        """
        محاسبه تعداد دروس هر رشته
        """
        return obj.course_set.count()

class ProfessorSerializer(serializers.ModelSerializer):
    """
    سریالایزر استاد
    """
    department_name = serializers.CharField(source='department.name', read_only=True)
    faculty_name = serializers.CharField(source='department.faculty.name', read_only=True)
    contact_info = serializers.SerializerMethodField()
    classes_count = serializers.SerializerMethodField()
    full_name = serializers.CharField(read_only=True)
    age = serializers.IntegerField(read_only=True)
    teaching_years = serializers.IntegerField(read_only=True)
    jalali_birth_date = serializers.CharField(read_only=True)
    jalali_employment_date = serializers.CharField(read_only=True)
    contract_type_display = serializers.CharField(source='get_contract_type_display', read_only=True)
    gender_display = serializers.CharField(source='get_gender_display', read_only=True)
    marital_status_display = serializers.CharField(source='get_marital_status_display', read_only=True)
    
    class Meta:
        model = Professor
        fields = '__all__'
        
    def get_contact_info(self, obj):
        """
        دریافت اطلاعات تماس استاد
        """
        from django.contrib.contenttypes.models import ContentType
        content_type = ContentType.objects.get_for_model(Professor)
        contact_infos = ContactInfo.objects.filter(
            content_type=content_type,
            object_id=obj.id
        )
        return ContactInfoSerializer(contact_infos, many=True).data
    
    def get_classes_count(self, obj):
        """
        محاسبه تعداد کلاس‌های تدریس شده توسط استاد
        """
        return obj.classoffering_set.count()

class StudentSerializer(serializers.ModelSerializer):
    """
    سریالایزر دانشجو
    """
    department_name = serializers.CharField(source='department.name', read_only=True)
    faculty_name = serializers.CharField(source='department.faculty.name', read_only=True)
    contact_info = serializers.SerializerMethodField()
    passed_courses_count = serializers.SerializerMethodField()
    failed_courses_count = serializers.SerializerMethodField()
    total_credits_earned = serializers.SerializerMethodField()
    remaining_credits = serializers.SerializerMethodField()
    gpa = serializers.SerializerMethodField()
    full_name = serializers.CharField(read_only=True)
    age = serializers.IntegerField(read_only=True)
    study_years = serializers.IntegerField(read_only=True)
    jalali_birth_date = serializers.CharField(read_only=True)
    jalali_admission_date = serializers.CharField(read_only=True)
    jalali_graduation_date = serializers.CharField(read_only=True)
    student_status_display = serializers.CharField(source='get_student_status_display', read_only=True)
    gender_display = serializers.CharField(source='get_gender_display', read_only=True)
    marital_status_display = serializers.CharField(source='get_marital_status_display', read_only=True)
    military_status_display = serializers.CharField(source='get_military_status_display', read_only=True)
    
    class Meta:
        model = Student
        fields = '__all__'
        
    def get_contact_info(self, obj):
        """
        دریافت اطلاعات تماس دانشجو
        """
        from django.contrib.contenttypes.models import ContentType
        content_type = ContentType.objects.get_for_model(Student)
        contact_infos = ContactInfo.objects.filter(
            content_type=content_type,
            object_id=obj.id
        )
        return ContactInfoSerializer(contact_infos, many=True).data
    
    def get_passed_courses_count(self, obj):
        """
        محاسبه تعداد دروس قبول شده
        """
        return obj.enrollment_set.filter(grade__gte=10).count()
    
    def get_failed_courses_count(self, obj):
        """
        محاسبه تعداد دروس مردود شده
        """
        return obj.enrollment_set.filter(grade__lt=10, grade__isnull=False).count()
    
    def get_total_credits_earned(self, obj):
        """
        محاسبه تعداد واحدهای گذرانده شده
        """
        passed_enrollments = obj.enrollment_set.filter(grade__gte=10)
        total_credits = sum(enrollment.class_offering.course.credits for enrollment in passed_enrollments)
        return total_credits
    
    def get_remaining_credits(self, obj):
        """
        محاسبه تعداد واحدهای باقی‌مانده
        """
        total_credits = obj.department.total_credits
        passed_credits = self.get_total_credits_earned(obj)
        return total_credits - passed_credits
    
    def get_gpa(self, obj):
        """
        محاسبه معدل کل
        """
        enrollments = obj.enrollment_set.filter(grade__isnull=False)
        if not enrollments.exists():
            return 0
            
        total_grade = 0
        total_credits = 0
        
        for enrollment in enrollments:
            course_credits = enrollment.class_offering.course.credits
            total_grade += enrollment.grade * course_credits
            total_credits += course_credits
            
        return round(total_grade / total_credits, 2) if total_credits > 0 else 0

class SemesterSerializer(serializers.ModelSerializer):
    """
    سریالایزر ترم تحصیلی
    """
    semester_type_display = serializers.CharField(source='get_semester_type_display', read_only=True)
    class_count = serializers.SerializerMethodField()
    jalali_start_date = serializers.CharField(read_only=True)
    jalali_end_date = serializers.CharField(read_only=True)
    is_current = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Semester
        fields = '__all__'
        
    def get_class_count(self, obj):
        """
        محاسبه تعداد کلاس‌های ارائه شده در ترم
        """
        return obj.classoffering_set.count()

class RoomSerializer(serializers.ModelSerializer):
    """
    سریالایزر اتاق
    """
    faculty_name = serializers.CharField(source='faculty.name', read_only=True)
    
    class Meta:
        model = Room
        fields = '__all__'

class CourseSerializer(serializers.ModelSerializer):
    """
    سریالایزر درس
    """
    department_name = serializers.CharField(source='department.name', read_only=True)
    faculty_name = serializers.CharField(source='department.faculty.name', read_only=True)
    prerequisites_info = serializers.SerializerMethodField()
    class_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = '__all__'
        
    def get_prerequisites_info(self, obj):
        """
        دریافت اطلاعات پیش‌نیازها
        """
        prereqs = obj.prerequisites.all()
        return [{'id': course.id, 'code': course.course_code, 'title': course.title} 
                for course in prereqs]
    
    def get_class_count(self, obj):
        """
        محاسبه تعداد کلاس‌های ارائه شده برای درس
        """
        return obj.classoffering_set.count()

class ClassSessionSerializer(serializers.ModelSerializer):
    """
    سریالایزر جلسه کلاس
    """
    room_number = serializers.CharField(source='room.room_number', read_only=True)
    faculty_name = serializers.CharField(source='room.faculty.name', read_only=True)
    weekday_display = serializers.CharField(source='get_weekday_display', read_only=True)
    
    class Meta:
        model = ClassSession
        fields = '__all__'

class ClassOfferingSerializer(serializers.ModelSerializer):
    """
    سریالایزر کلاس ارائه شده
    """
    course_title = serializers.CharField(source='course.title', read_only=True)
    course_credits = serializers.IntegerField(source='course.credits', read_only=True)
    professor_name = serializers.CharField(source='professor.full_name', read_only=True)
    semester_name = serializers.SerializerMethodField()
    enrolled_count = serializers.IntegerField(read_only=True)
    remaining_capacity = serializers.IntegerField(read_only=True)
    average_grade = serializers.SerializerMethodField()
    sessions = serializers.SerializerMethodField()
    
    class Meta:
        model = ClassOffering
        fields = '__all__'
        
    def get_semester_name(self, obj):
        """
        دریافت نام ترم به صورت خوانا
        """
        return str(obj.semester)
    
    def get_average_grade(self, obj):
        """
        محاسبه میانگین نمرات کلاس
        """
        average = obj.enrollment_set.filter(grade__isnull=False).aggregate(avg=Avg('grade'))
        return round(average['avg'], 2) if average['avg'] is not None else None
    
    def get_sessions(self, obj):
        """
        دریافت اطلاعات جلسات کلاس
        """
        sessions = obj.classsession_set.all()
        return ClassSessionSerializer(sessions, many=True).data

class EnrollmentSerializer(serializers.ModelSerializer):
    """
    سریالایزر ثبت‌نام
    """
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    student_code = serializers.CharField(source='student.student_code', read_only=True)
    class_title = serializers.CharField(source='class_offering.course.title', read_only=True)
    semester_name = serializers.CharField(source='class_offering.semester', read_only=True)
    professor_name = serializers.CharField(source='class_offering.professor.full_name', read_only=True)
    credits = serializers.IntegerField(source='class_offering.course.credits', read_only=True)
    has_passed = serializers.BooleanField(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    jalali_enrollment_date = serializers.CharField(read_only=True)
    
    class Meta:
        model = Enrollment
        fields = '__all__' 