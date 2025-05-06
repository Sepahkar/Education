from django.shortcuts import render, redirect
from .models import (
    Faculty, Department, Professor, Student, Semester, 
    Room, Course, ClassOffering, ClassSession, Enrollment, ContactInfo, STUDENT_STATUS_CHOICES
)
from django.views.generic import TemplateView
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.contrib.auth import authenticate
from django.contrib import messages
from django.db.models import Sum, Avg, Count
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
import random
import json
from decimal import Decimal

# تابع کمکی برای تبدیل Decimal به float برای سریالایز کردن به JSON
def decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError("Object of type %s is not JSON serializable" % type(obj).__name__)

# Create your views here.

def welcome(request):
    """
    صفحه خوش‌آمدگویی سیستم
    """
    return render(request, 'EducationApp/welcome.html')

class ObtainAuthTokenView(APIView):
    """
    دریافت توکن احراز هویت
    """
    permission_classes = []
    
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            return Response(
                {'error': 'هر دو فیلد نام کاربری و رمز عبور الزامی هستند'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = authenticate(username=username, password=password)
        
        if not user:
            return Response(
                {'error': 'نام کاربری یا رمز عبور اشتباه است'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key})

class ApiDocsView(TemplateView):
    """
    صفحه مستندات API با امکان تست درخواست‌ها
    """
    template_name = 'EducationApp/api_docs.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # تعریف API های موجود به همراه توضیحات
        api_endpoints = [
            {
                'model_name': 'Faculty',
                'persian_name': 'دانشکده',
                'description': 'مدیریت اطلاعات دانشکده‌های دانشگاه',
                'base_url': '/EducationApp/api/faculties/',
                'methods': ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'],
                'fields': ['id', 'code', 'name', 'establishment_date', 'department_count'],
            },
            {
                'model_name': 'Department',
                'persian_name': 'رشته تحصیلی',
                'description': 'مدیریت اطلاعات رشته‌های تحصیلی دانشگاه',
                'base_url': '/EducationApp/api/departments/',
                'methods': ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'],
                'fields': ['id', 'code', 'name', 'faculty', 'total_credits'],
            },
            {
                'model_name': 'Professor',
                'persian_name': 'استاد',
                'description': 'مدیریت اطلاعات اساتید دانشگاه',
                'base_url': '/EducationApp/api/professors/',
                'methods': ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'],
                'fields': ['id', 'first_name', 'last_name', 'professor_code', 'department'],
            },
            {
                'model_name': 'Student',
                'persian_name': 'دانشجو',
                'description': 'مدیریت اطلاعات دانشجویان دانشگاه',
                'base_url': '/EducationApp/api/students/',
                'methods': ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'],
                'fields': ['id', 'first_name', 'last_name', 'student_code', 'department'],
            },
            {
                'model_name': 'Semester',
                'persian_name': 'ترم تحصیلی',
                'description': 'مدیریت اطلاعات ترم‌های تحصیلی دانشگاه',
                'base_url': '/EducationApp/api/semesters/',
                'methods': ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'],
                'fields': ['id', 'academic_year', 'semester_type', 'start_date', 'end_date'],
            },
            {
                'model_name': 'Room',
                'persian_name': 'اتاق',
                'description': 'مدیریت اطلاعات اتاق‌های دانشگاه',
                'base_url': '/EducationApp/api/rooms/',
                'methods': ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'],
                'fields': ['id', 'room_number', 'faculty', 'capacity', 'floor'],
            },
            {
                'model_name': 'Course',
                'persian_name': 'درس',
                'description': 'مدیریت اطلاعات دروس دانشگاه',
                'base_url': '/EducationApp/api/courses/',
                'methods': ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'],
                'fields': ['id', 'course_code', 'title', 'department', 'credits'],
            },
            {
                'model_name': 'ClassOffering',
                'persian_name': 'کلاس (ارائه درس)',
                'description': 'مدیریت اطلاعات کلاس‌های ارائه شده در ترم‌های مختلف',
                'base_url': '/EducationApp/api/class-offerings/',
                'methods': ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'],
                'fields': ['id', 'course', 'semester', 'professor', 'class_code', 'capacity'],
            },
            {
                'model_name': 'ClassSession',
                'persian_name': 'جلسه کلاس',
                'description': 'مدیریت اطلاعات جلسات کلاس و برنامه زمانی',
                'base_url': '/EducationApp/api/class-sessions/',
                'methods': ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'],
                'fields': ['id', 'class_offering', 'room', 'weekday', 'start_time', 'end_time'],
            },
            {
                'model_name': 'Enrollment',
                'persian_name': 'ثبت‌نام',
                'description': 'مدیریت اطلاعات ثبت‌نام دانشجویان در کلاس‌ها',
                'base_url': '/EducationApp/api/enrollments/',
                'methods': ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'],
                'fields': ['id', 'student', 'class_offering', 'status', 'grade'],
            },
            {
                'model_name': 'ContactInfo',
                'persian_name': 'اطلاعات تماس',
                'description': 'مدیریت اطلاعات تماس اساتید و دانشجویان',
                'base_url': '/EducationApp/api/contacts/',
                'methods': ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'],
                'fields': ['id', 'content_type', 'object_id', 'contact_type', 'value'],
            },
        ]
        
        context['api_endpoints'] = api_endpoints
        return context

# لیست تصاویر پروفایل دانشجویان
PROFILE_IMAGES = [
    "https://images.unsplash.com/photo-1494790108377-be9c29b29330",
    "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d",
    "https://images.unsplash.com/photo-1534528741775-53994a69daeb",
    "https://images.unsplash.com/photo-1539571696357-5a69c17a67c6",
    "https://images.unsplash.com/photo-1517841905240-472988babdf9",
    "https://images.unsplash.com/photo-1488161628813-04466f872be2",
    "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde",
    "https://images.unsplash.com/photo-1573497019940-1c28c88b4f3e",
    "https://images.unsplash.com/photo-1438761681033-6461ffad8d80",
    "https://images.unsplash.com/photo-1500648767791-00dcc994a43e",
    "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d",
    "https://images.unsplash.com/photo-1527980965255-d3b416303d12",
    "https://images.unsplash.com/photo-1544005313-94ddf0286df2",
    "https://images.unsplash.com/photo-1532074205216-d0e1f4b87368",
    "https://images.unsplash.com/photo-1558898479-33c0057a5d12",
    "https://images.unsplash.com/photo-1499996860823-5214fcc65f8f",
    "https://images.unsplash.com/photo-1542103749-8ef59b94f47e",
    "https://images.unsplash.com/photo-1544348817-5f2cf14b88c8",
    "https://images.unsplash.com/photo-1546539782-6fc531453083",
    "https://images.unsplash.com/photo-1546967191-fdfb13ed6b1e",
    "https://images.unsplash.com/photo-1552058544-f2b08422138a",
    "https://images.unsplash.com/photo-1555952517-2e8e729e0b44",
    "https://images.unsplash.com/photo-1571442463800-1337d7af9d2f",
    "https://images.unsplash.com/photo-1552374196-c4e7ffc6e126",
    "https://images.unsplash.com/photo-1541647376583-8934aaf3448a",
    "https://images.unsplash.com/photo-1548142813-c348350df52b",
    "https://images.unsplash.com/photo-1499651681375-8afc5a4db253",
    "https://images.unsplash.com/photo-1547212371-eb5e6a4b590c",
    "https://images.unsplash.com/photo-1503443207922-dff7d543fd0e",
    "https://images.unsplash.com/photo-1527203561188-dae1bc1a417f",
    "https://images.unsplash.com/photo-1544717302-de2939b7ef71",
    "https://images.unsplash.com/photo-1559582454-4d63d28485f5",
    "https://images.unsplash.com/photo-1545167622-3a6ac756afa4",
    "https://images.unsplash.com/photo-1564460576398-ef55d99548b2",
    "https://images.unsplash.com/photo-1545167622-3a6ac756afa4",
    "https://images.unsplash.com/photo-1501196354995-cbb51c65aaea",
    "https://images.unsplash.com/photo-1530785602389-07594beb8b73",
    "https://images.unsplash.com/photo-1531427186611-ecfd6d936c79",
    "https://images.unsplash.com/photo-1520813792240-56fc4a3765a7",
    "https://images.unsplash.com/photo-1568822617270-2c1579f8dfe2",
    "https://images.unsplash.com/photo-1492447166138-50c3889fccb1",
    "https://images.unsplash.com/photo-1507537297725-24a1c029d3ca",
    "https://images.unsplash.com/photo-1522075469751-3a6694fb2f61",
    "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae",
    "https://images.unsplash.com/photo-1528892952291-009c663ce843",
    "https://images.unsplash.com/photo-1569173112611-52a7cd38bea9",
    "https://images.unsplash.com/photo-1553514029-1318c9127859",
    "https://images.unsplash.com/photo-1566753323558-f4e0952af115",
    "https://images.unsplash.com/photo-1518020382113-a7e8fc38eac9",
    "https://images.unsplash.com/photo-1560250097-0b93528c311a"
]

# لیست تصاویر پس‌زمینه
BACKGROUND_IMAGES = [
    "https://images.unsplash.com/photo-1606761568499-6d2451b23c66",  # دانشگاه
    "https://images.unsplash.com/photo-1541339907198-e08756dedf3f",  # کتابخانه
    "https://images.unsplash.com/photo-1523050854058-8df90110c9f1",  # کلاس درس
    "https://images.unsplash.com/photo-1498243691581-b145c3f54a5a",  # دانشگاه مدرن
    "https://images.unsplash.com/photo-1497633762265-9d179a990aa6",  # کتاب‌ها
    "https://images.unsplash.com/photo-1535982330050-f1c2fb79ff78",  # پردیس دانشگاه
    "https://images.unsplash.com/photo-1599687266725-0d4d52b8564c",  # محیط مطالعه
    "https://images.unsplash.com/photo-1576267423048-15c0040fec78",  # کامپیوتر و تحصیلات
    "https://images.unsplash.com/photo-1564981797816-1043ecbb0cc7",  # محیط کلاس
    "https://images.unsplash.com/photo-1427504494785-3a9ca7044f45"   # ساختمان دانشگاه
]

def student_login(request):
    """
    صفحه لاگین دانشجویان
    """
    if request.method == 'POST':
        student_code = request.POST.get('student_code')
        password = request.POST.get('password')
        
        if not student_code or not password:
            messages.error(request, 'شماره دانشجویی و رمز عبور الزامی هستند')
            return render(request, 'EducationApp/student_login.html')
        
        try:
            student = Student.objects.get(student_code=student_code)
            
            # بررسی وضعیت دانشجو
            if student.student_status == 'GR':
                messages.error(request, 'دانشجوی فارغ‌التحصیل نمی‌تواند وارد شود')
                return render(request, 'EducationApp/student_login.html')
                
            # بررسی کلمه عبور
            if password != '123456':
                messages.error(request, 'رمز عبور اشتباه است')
                return render(request, 'EducationApp/student_login.html')
                
            # لاگین موفق
            request.session['student_id'] = student.id
            request.session['student_name'] = student.full_name
            
            # انتخاب تصویر پروفایل تصادفی
            profile_image = random.choice(PROFILE_IMAGES)
            request.session['profile_image'] = profile_image
            
            return redirect('student_dashboard')
            
        except Student.DoesNotExist:
            messages.error(request, 'دانشجویی با این شماره دانشجویی یافت نشد')
            return render(request, 'EducationApp/student_login.html')
    
    return render(request, 'EducationApp/student_login.html', {
        'background_image': random.choice(BACKGROUND_IMAGES)
    })

def student_logout(request):
    """
    خروج از حساب کاربری دانشجو
    """
    # پاک کردن اطلاعات نشست
    if 'student_id' in request.session:
        del request.session['student_id']
    if 'student_name' in request.session:
        del request.session['student_name']
    if 'profile_image' in request.session:
        del request.session['profile_image']
    
    messages.success(request, 'با موفقیت خارج شدید')
    return redirect('student_login')

def student_dashboard(request):
    """
    داشبورد دانشجو
    """
    # بررسی لاگین بودن دانشجو
    if 'student_id' not in request.session:
        messages.error(request, 'لطفا ابتدا وارد شوید')
        return redirect('student_login')
    
    student_id = request.session['student_id']
    
    try:
        student = Student.objects.get(id=student_id)
        
        # محاسبه تعداد واحدهای پاس شده
        passed_enrollments = Enrollment.objects.filter(
            student=student,
            grade__gte=10
        )
        
        passed_credits = sum(enrollment.class_offering.course.credits for enrollment in passed_enrollments)
        
        # محاسبه تعداد واحدهای باقی‌مانده (فرض: نیاز به 140 واحد)
        total_credits_required = 140
        remaining_credits = max(0, total_credits_required - passed_credits)
        
        # محاسبه معدل
        total_weighted_grade = 0
        total_credits_with_grade = 0
        
        for enrollment in passed_enrollments:
            course_credits = enrollment.class_offering.course.credits
            total_weighted_grade += enrollment.grade * course_credits
            total_credits_with_grade += course_credits
        
        gpa = round(total_weighted_grade / total_credits_with_grade, 2) if total_credits_with_grade > 0 else 0
        
        # اطلاعات ترم جاری
        current_semester = Semester.objects.filter(is_active=True).first()
        
        # اطلاعات برای نمودارها
        chart_data = {
            'credits': {
                'passed': passed_credits,
                'remaining': remaining_credits
            },
            'gpa': gpa,
            'standard_gpas': [12, 15, 18, 20]  # مقادیر استاندارد برای مقایسه
        }
        
        context = {
            'student': student,
            'passed_credits': passed_credits,
            'remaining_credits': remaining_credits,
            'gpa': gpa,
            'chart_data': json.dumps(chart_data, default=decimal_default),
            'profile_image': request.session.get('profile_image', PROFILE_IMAGES[0]),
            'current_semester': current_semester,
            'background_image': random.choice(BACKGROUND_IMAGES)
        }
        
        return render(request, 'EducationApp/student_dashboard.html', context)
        
    except Student.DoesNotExist:
        messages.error(request, 'اطلاعات دانشجو یافت نشد')
        return redirect('student_login')

def student_profile(request):
    """
    اطلاعات شخصی دانشجو
    """
    # بررسی لاگین بودن دانشجو
    if 'student_id' not in request.session:
        messages.error(request, 'لطفا ابتدا وارد شوید')
        return redirect('student_login')
    
    student_id = request.session['student_id']
    
    try:
        student = Student.objects.get(id=student_id)
        
        # دریافت اطلاعات تماس دانشجو
        from django.contrib.contenttypes.models import ContentType
        content_type = ContentType.objects.get_for_model(Student)
        contact_info = ContactInfo.objects.filter(
            content_type=content_type,
            object_id=student.id
        )
        
        context = {
            'student': student,
            'contact_info': contact_info,
            'profile_image': request.session.get('profile_image', PROFILE_IMAGES[0]),
            'background_image': random.choice(BACKGROUND_IMAGES)
        }
        
        return render(request, 'EducationApp/student_profile.html', context)
        
    except Student.DoesNotExist:
        messages.error(request, 'اطلاعات دانشجو یافت نشد')
        return redirect('student_login')

def course_selection(request):
    """
    انتخاب واحد دانشجو
    """
    # بررسی لاگین بودن دانشجو
    if 'student_id' not in request.session:
        messages.error(request, 'لطفا ابتدا وارد شوید')
        return redirect('student_login')
    
    student_id = request.session['student_id']
    
    try:
        student = Student.objects.get(id=student_id)
        
        # یافتن ترم جاری
        current_semester = Semester.objects.filter(is_active=True).first()
        
        if not current_semester:
            messages.error(request, 'در حال حاضر ترم فعالی وجود ندارد')
            return redirect('student_dashboard')
        
        # دریافت کلاس‌های ارائه شده در ترم جاری
        class_offerings = ClassOffering.objects.filter(semester=current_semester)
        
        # دریافت ثبت‌نام‌های فعلی دانشجو در ترم جاری
        current_enrollments = Enrollment.objects.filter(
            student=student,
            class_offering__semester=current_semester
        )
        
        # محاسبه تعداد واحدهای انتخاب شده در ترم جاری
        current_credits = sum(enrollment.class_offering.course.credits for enrollment in current_enrollments)
        
        # حداکثر تعداد واحد مجاز
        max_credits = 20
        
        # لیست دروس پاس شده
        passed_courses = Enrollment.objects.filter(
            student=student,
            grade__gte=10
        ).values_list('class_offering__course__id', flat=True)
        
        # پردازش ثبت‌نام در کلاس
        if request.method == 'POST':
            class_offering_id = request.POST.get('class_offering_id')
            
            if not class_offering_id:
                messages.error(request, 'کلاس نامعتبر')
                return redirect('course_selection')
                
            try:
                class_offering = ClassOffering.objects.get(id=class_offering_id)
                
                # بررسی اینکه آیا دانشجو قبلاً این درس را پاس کرده است
                if class_offering.course.id in passed_courses:
                    messages.error(request, 'شما قبلاً این درس را پاس کرده‌اید')
                    return redirect('course_selection')
                
                # بررسی اینکه آیا دانشجو قبلاً در این کلاس ثبت‌نام کرده است
                if Enrollment.objects.filter(student=student, class_offering=class_offering).exists():
                    messages.error(request, 'شما قبلاً در این کلاس ثبت‌نام کرده‌اید')
                    return redirect('course_selection')
                
                # بررسی محدودیت تعداد واحد
                if current_credits + class_offering.course.credits > max_credits:
                    messages.error(request, f'حداکثر تعداد واحد مجاز {max_credits} واحد است')
                    return redirect('course_selection')
                
                # بررسی ظرفیت کلاس
                if class_offering.enrolled_count >= class_offering.capacity:
                    messages.error(request, 'ظرفیت این کلاس تکمیل شده است')
                    return redirect('course_selection')
                
                # ایجاد ثبت‌نام جدید
                enrollment = Enrollment(
                    student=student,
                    class_offering=class_offering,
                    status='P'  # وضعیت در انتظار تأیید
                )
                enrollment.save()
                
                messages.success(request, 'درس با موفقیت انتخاب شد')
                current_credits += class_offering.course.credits
                return redirect('course_selection')
                
            except ClassOffering.DoesNotExist:
                messages.error(request, 'کلاس مورد نظر یافت نشد')
                return redirect('course_selection')
        
        # دریافت لیست کلاس‌های ثبت‌نام شده دانشجو
        enrolled_classes = [enrollment.class_offering.id for enrollment in current_enrollments]
        
        context = {
            'student': student,
            'current_semester': current_semester,
            'class_offerings': class_offerings,
            'current_enrollments': current_enrollments,
            'current_credits': current_credits,
            'max_credits': max_credits,
            'enrolled_classes': enrolled_classes,
            'profile_image': request.session.get('profile_image', PROFILE_IMAGES[0]),
            'background_image': random.choice(BACKGROUND_IMAGES)
        }
        
        return render(request, 'EducationApp/course_selection.html', context)
        
    except Student.DoesNotExist:
        messages.error(request, 'اطلاعات دانشجو یافت نشد')
        return redirect('student_login')
