from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.pagination import PageNumberPagination
from .models import Faculty, Major, Student, Professor, Course, Term, Room, Class, Enrollment, CourseAssignment, ContactInfo
from .serializers import (
    FacultySerializer, MajorSerializer, StudentSerializer, ProfessorSerializer,
    CourseSerializer, TermSerializer, RoomSerializer, ClassSerializer,
    EnrollmentSerializer, CourseAssignmentSerializer, ContactInfoSerializer
)
from django.shortcuts import render

class StandardPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 100

class FacultyViewSet(viewsets.ModelViewSet):
    """
    API برای مدیریت دانشکده‌ها
    - GET /api/faculties/: لیست تمام دانشکده‌ها یا اطلاعات یک دانشکده با ID
    - POST /api/faculties/: ایجاد دانشکده جدید
    - PUT /api/faculties/<id>/: به‌روزرسانی کامل دانشکده
    - PATCH /api/faculties/<id>/: به‌روزرسانی جزئی دانشکده
    - DELETE /api/faculties/<id>/: حذف دانشکده
    پاسخ‌ها:
    - 200: موفقیت
    - 400: خطای ورودی
    - 404: دانشکده یافت نشد
    """
    queryset = Faculty.objects.all()
    serializer_class = FacultySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = StandardPagination

class MajorViewSet(viewsets.ModelViewSet):
    """
    API برای مدیریت رشته‌ها
    - GET /api/majors/: لیست تمام رشته‌ها یا اطلاعات یک رشته با ID
    - POST /api/majors/: ایجاد رشته جدید
    - PUT /api/majors/<id>/: به‌روزرسانی کامل رشته
    - PATCH /api/majors/<id>/: به‌روزرسانی جزئی رشته
    - DELETE /api/majors/<id>/: حذف رشته
    پاسخ‌ها:
    - 200: موفقیت
    - 400: خطای ورودی
    - 404: رشته یافت نشد
    """
    queryset = Major.objects.all()
    serializer_class = MajorSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = StandardPagination

class StudentViewSet(viewsets.ModelViewSet):
    """
    API برای مدیریت دانشجویان
    - GET /api/students/: لیست تمام دانشجویان یا اطلاعات یک دانشجو با ID
    - POST /api/students/: ایجاد دانشجوی جدید
    - PUT /api/students/<id>/: به‌روزرسانی کامل دانشجو
    - PATCH /api/students/<id>/: به‌روزرسانی جزئی دانشجو
    - DELETE /api/students/<id>/: حذف دانشجو
    پاسخ‌ها:
    - 200: موفقیت
    - 400: خطای ورودی
    - 404: دانشجو یافت نشد
    """
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = StandardPagination

class ProfessorViewSet(viewsets.ModelViewSet):
    """
    API برای مدیریت اساتید
    - GET /api/professors/: لیست تمام اساتید یا اطلاعات یک استاد با ID
    - POST /api/professors/: ایجاد استاد جدید
    - PUT /api/professors/<id>/: به‌روزرسانی کامل استاد
    - PATCH /api/professors/<id>/: به‌روزرسانی جزئی استاد
    - DELETE /api/professors/<id>/: حذف استاد
    پاسخ‌ها:
    - 200: موفقیت
    - 400: خطای ورودی
    - 404: استاد یافت نشد
    """
    queryset = Professor.objects.all()
    serializer_class = ProfessorSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = StandardPagination

class CourseViewSet(viewsets.ModelViewSet):
    """
    API برای مدیریت دروس
    - GET /api/courses/: لیست تمام دروس یا اطلاعات یک درس با ID
    - POST /api/courses/: ایجاد درس جدید
    - PUT /api/courses/<id>/: به‌روزرسانی کامل درس
    - PATCH /api/courses/<id>/: به‌روزرسانی جزئی درس
    - DELETE /api/courses/<id>/: حذف درس
    پاسخ‌ها:
    - 200: موفقیت
    - 400: خطای ورودی
    - 404: درس یافت نشد
    """
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = StandardPagination

class TermViewSet(viewsets.ModelViewSet):
    """
    API برای مدیریت ترم‌ها
    - GET /api/terms/: لیست تمام ترم‌ها یا اطلاعات یک ترم با ID
    - POST /api/terms/: ایجاد ترم جدید
    - PUT /api/terms/<id>/: به‌روزرسانی کامل ترم
    - PATCH /api/terms/<id>/: به‌روزرسانی جزئی ترم
    - DELETE /api/terms/<id>/: حذف ترم
    پاسخ‌ها:
    - 200: موفقیت
    - 400: خطای ورودی
    - 404: ترم یافت نشد
    """
    queryset = Term.objects.all()
    serializer_class = TermSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = StandardPagination

class RoomViewSet(viewsets.ModelViewSet):
    """
    API برای مدیریت اتاق‌ها
    - GET /api/rooms/: لیست تمام اتاق‌ها یا اطلاعات یک اتاق با ID
    - POST /api/rooms/: ایجاد اتاق جدید
    - PUT /api/rooms/<id>/: به‌روزرسانی کامل اتاق
    - PATCH /api/rooms/<id>/: به‌روزرسانی جزئی اتاق
    - DELETE /api/rooms/<id>/: حذف اتاق
    پاسخ‌ها:
    - 200: موفقیت
    - 400: خطای ورودی
    - 404: اتاق یافت نشد
    """
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = StandardPagination

class ClassViewSet(viewsets.ModelViewSet):
    """
    API برای مدیریت کلاس‌ها
    - GET /api/classes/: لیست تمام کلاس‌ها یا اطلاعات یک کلاس با ID
    - POST /api/classes/: ایجاد کلاس جدید
    - PUT /api/classes/<id>/: به‌روزرسانی کامل کلاس
    - PATCH /api/classes/<id>/: به‌روزرسانی جزئی کلاس
    - DELETE /api/classes/<id>/: حذف کلاس
    پاسخ‌ها:
    - 200: موفقیت
    - 400: خطای ورودی
    - 404: کلاس یافت نشد
    """
    queryset = Class.objects.all()
    serializer_class = ClassSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = StandardPagination

class EnrollmentViewSet(viewsets.ModelViewSet):
    """
    API برای مدیریت ثبت‌نام‌ها
    - GET /api/enrollments/: لیست تمام ثبت‌نام‌ها یا اطلاعات یک ثبت‌نام با ID
    - POST /api/enrollments/: ایجاد ثبت‌نام جدید
    - PUT /api/enrollments/<id>/: به‌روزرسانی کامل ثبت‌نام
    - PATCH /api/enrollments/<id>/: به‌روزرسانی جزئی ثبت‌نام
    - DELETE /api/enrollments/<id>/: حذف ثبت‌نام
    پاسخ‌ها:
    - 200: موفقیت
    - 400: خطای ورودی
    - 404: ثبت‌نام یافت نشد
    """
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = StandardPagination

class CourseAssignmentViewSet(viewsets.ModelViewSet):
    """
    API برای مدیریت تخصیص دروس
    - GET /api/course-assignments/: لیست تمام تخصیص‌ها یا اطلاعات یک تخصیص با ID
    - POST /api/course-assignments/: ایجاد تخصیص جدید
    - PUT /api/course-assignments/<id>/: به‌روزرسانی کامل تخصیص
    - PATCH /api/course-assignments/<id>/: به‌روزرسانی جزئی تخصیص
    - DELETE /api/course-assignments/<id>/: حذف تخصیص
    پاسخ‌ها:
    - 200: موفقیت
    - 400: خطای ورودی
    - 404: تخصیص یافت نشد
    """
    queryset = CourseAssignment.objects.all()
    serializer_class = CourseAssignmentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = StandardPagination

class ContactInfoViewSet(viewsets.ModelViewSet):
    """
    API برای مدیریت اطلاعات تماس
    - GET /api/contact-infos/: لیست تمام اطلاعات تماس یا اطلاعات یک تماس با ID
    - POST /api/contact-infos/: ایجاد اطلاعات تماس جدید
    - PUT /api/contact-infos/<id>/: به‌روزرسانی کامل اطلاعات تماس
    - PATCH /api/contact-infos/<id>/: به‌روزرسانی جزئی اطلاعات تماس
    - DELETE /api/contact-infos/<id>/: حذف اطلاعات تماس
    پاسخ‌ها:
    - 200: موفقیت
    - 400: خطای ورودی
    - 404: اطلاعات تماس یافت نشد
    """
    queryset = ContactInfo.objects.all()
    serializer_class = ContactInfoSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = StandardPagination

def api_docs(request):
    """
    نمایش صفحه مستندات API
    """
    return render(request, 'api_docs.html')

def welcome(request):
    """
    نمایش صفحه خوش‌آمدگویی
    """
    return render(request, 'EducationApp/welcome.html')