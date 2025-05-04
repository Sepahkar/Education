from django.utils import timezone
from datetime import time
from random import choice, randint, shuffle
import numpy as np
from django.contrib.contenttypes.models import ContentType
from .models import Faculty, Major, Student, Professor, Course, Term, Room, Class, Enrollment, CourseAssignment, ContactInfo

def generate_national_id():
    """
    تولید کد ملی معتبر 10 رقمی با رقم کنترلی
    """
    digits = [randint(0, 9) for _ in range(9)]
    weights = [10, 9, 8, 7, 6, 5, 4, 3, 2]
    total = sum(d * w for d, w in zip(digits, weights))
    remainder = total % 11
    control_digit = remainder if remainder < 2 else 11 - remainder
    digits.append(control_digit)
    return ''.join(map(str, digits))

def generate_sample_data():
    """
    اسکریپت برای تولید داده‌های نمونه با شروط مشخص‌شده
    """
    # لیست اسامی غیرتکراری
    first_names_male = [
        'علی', 'محمد', 'حسین', 'رضا', 'مهدی', 'احمد', 'امیر', 'سجاد', 'جواد', 'حسن',
        'یاسر', 'کیوان', 'نیما', 'پوریا', 'بهرام', 'سامان', 'فرهاد', 'کاوه', 'رامین', 'بهزاد'
    ]
    first_names_female = [
        'فاطمه', 'زهرا', 'مریم', 'نرگس', 'سمیه', 'لیلا', 'شیما', 'مهسا', 'پریسا', 'الهام',
        'سارا', 'نازنین', 'رها', 'آتنا', 'مینا', 'شیدا', 'بهناز', 'نگار', 'رویا', 'پریناز'
    ]
    last_names = [
        'احمدی', 'محمدی', 'رضایی', 'کریمی', 'علوی', 'حسینی', 'موسوی', 'رحیمی', 'زارعی', 'شریفی',
        'یزدانی', 'کاظمی', 'نعمتی', 'قاسمی', 'صادقی', 'جعفری', 'اکبری', 'طاهری', 'امینی', 'بهرامی'
    ]

    # لیست آدرس‌های واقعی در تهران
    tehran_addresses = [
        'تهران، خیابان ولیعصر، نبش کوچه مهر',
        'تهران، خیابان انقلاب، روبروی دانشگاه تهران',
        'تهران، خیابان آزادی، پلاک ۱۲۳',
        'تهران، میدان ونک، خیابان ملاصدرا',
        'تهران، خیابان شریعتی، نرسیده به پل صدر',
        'تهران، خیابان پاسداران، نبش بوستان دوم',
        'تهران، میدان تجریش، خیابان ولیعصر',
        'تهران، خیابان جمهوری، پلاک ۴۵۶',
        'تهران، خیابان کریمخان، نبش خیابان ویلا',
        'تهران، بلوار کشاورز، پلاک ۷۸'
    ]

    # بارگذاری یا ایجاد دانشکده‌ها
    faculties = list(Faculty.objects.all())
    faculty_names = [
        'مهندسی', 'علوم پایه', 'علوم انسانی', 'هنر', 'پزشکی',
        'اقتصاد', 'کشاورزی', 'تربیت بدنی', 'حقوق', 'مدیریت'
    ]
    existing_codes = set(faculty.code for faculty in faculties)
    for i, name in enumerate(faculty_names, 1):
        code = f'F{i:03d}'
        if code not in existing_codes:
            faculty = Faculty.objects.create(name=name, code=code)
            faculties.append(faculty)
            existing_codes.add(code)

    # بررسی وجود حداقل یک دانشکده
    if not faculties:
        raise ValueError("هیچ دانشکده‌ای وجود ندارد. لطفاً دیتابیس را بررسی کنید.")

    # ایجاد رشته‌ها
    majors = list(Major.objects.all())
    major_names = [
        'مهندسی کامپیوتر', 'مهندسی برق', 'مهندسی مکانیک', 'مهندسی عمران', 'مهندسی شیمی',
        'ریاضی', 'فیزیک', 'شیمی', 'زیست‌شناسی', 'آمار',
        'روان‌شناسی', 'جامعه‌شناسی', 'علوم سیاسی', 'تاریخ', 'زبان انگلیسی',
        'نقاشی', 'موسیقی', 'گرافیک', 'معماری', 'تئاتر',
        'پزشکی عمومی', 'دندانپزشکی', 'داروسازی', 'پرستاری', 'علوم آزمایشگاهی',
        'اقتصاد', 'مدیریت بازرگانی', 'حسابداری', 'حقوق', 'مدیریت دولتی'
    ]
    existing_codes = set(major.code for major in majors)
    for i, name in enumerate(major_names[:30], 1):
        code = f'M{i:03d}'
        if code not in existing_codes:
            major = Major.objects.create(
                name=name,
                code=code,
                faculty=choice(faculties)
            )
            majors.append(major)
            existing_codes.add(code)

    # ایجاد ترم‌ها (1398 تا 1403، پاییز و بهار)
    terms = list(Term.objects.all())
    for year in range(1398, 1404):
        for season in ['F', 'S']:
            if not Term.objects.filter(year=str(year), season=season).exists():
                term = Term.objects.create(
                    year=str(year),
                    season=season,
                    is_current=(year == 1403 and season == 'F')
                )
                terms.append(term)

    # ایجاد اتاق‌ها
    rooms = list(Room.objects.all())
    existing_names = set(room.name for room in rooms)
    for i in range(20):
        name = f'R{i+1:03d}'
        if name not in existing_names:
            room = Room.objects.create(
                name=name,
                building=choice(['ساختمان مهندسی', 'ساختمان علوم', 'ساختمان هنر', 'ساختمان پزشکی']),
                capacity=randint(20, 50)
            )
            rooms.append(room)
            existing_names.add(name)

    # ایجاد اساتید
    professors = list(Professor.objects.all())
    professor_ids = set(f'{p.first_name} {p.last_name}' for p in professors)
    existing_national_ids = set(p.national_id for p in professors)
    for i in range(100 - len(professors)):
        gender = choice(['M', 'F'])
        first_names = first_names_male if gender == 'M' else first_names_female
        first_name = choice(first_names)
        last_name = choice(last_names)
        
        while f'{first_name} {last_name}' in professor_ids:
            first_name = choice(first_names)
            last_name = choice(last_names)
        professor_ids.add(f'{first_name} {last_name}')

        national_id = generate_national_id()
        while national_id in existing_national_ids:
            national_id = generate_national_id()
        existing_national_ids.add(national_id)

        professor = Professor.objects.create(
            first_name=first_name,
            last_name=last_name,
            national_id=national_id,
            birth_date=f'135{randint(0,5)}/0{randint(1,9)}/{randint(10,28):02d}',
            birth_place='تهران',
            father_name=choice(['علی', 'حسین', 'محمد', 'رضا']),
            id_number=f'PID{i+1:04d}',
            gender=gender,
            marital_status=choice(['S', 'M']),
            address=choice(tehran_addresses),
            professor_id=f'P{i+1:04d}',
            faculty=choice(faculties),
            contract_type=choice(['F', 'P'])
        )
        ContactInfo.objects.create(
            content_type=ContentType.objects.get_for_model(Professor),
            object_id=professor.id,
            contact_type='M',
            value=f'+989{randint(10000000, 99999999)}'
        )
        ContactInfo.objects.create(
            content_type=ContentType.objects.get_for_model(Professor),
            object_id=professor.id,
            contact_type='E',
            value=f'prof{i+1}@university.ac.ir'
        )
        professors.append(professor)

    # ایجاد دانشجویان
    students = list(Student.objects.all())
    student_ids = set(f'{s.first_name} {s.last_name}' for s in students)
    existing_national_ids = set(s.national_id for s in students)
    for i in range(1000 - len(students)):
        gender = choice(['M', 'F'])
        first_names = first_names_male if gender == 'M' else first_names_female
        first_name = choice(first_names)
        last_name = choice(last_names)
        
        while f'{first_name} {last_name}' in student_ids:
            first_name = choice(first_names)
            last_name = choice(last_names)
        student_ids.add(f'{first_name} {last_name}')

        national_id = generate_national_id()
        while national_id in existing_national_ids:
            national_id = generate_national_id()
        existing_national_ids.add(national_id)

        entry_year = str(randint(1398, 1403))
        student = Student.objects.create(
            first_name=first_name,
            last_name=last_name,
            national_id=national_id,
            birth_date=f'137{randint(5,8)}/0{randint(1,9)}/{randint(10,28):02d}',
            birth_place='تهران',
            father_name=choice(['علی', 'حسین', 'محمد', 'رضا']),
            id_number=f'SID{i+1:04d}',
            gender=gender,
            marital_status='S',
            address=choice(tehran_addresses),
            student_id=f'S{i+1:04d}',
            major=choice(majors),
            entry_year=entry_year,
            military_status=choice(['E', 'P', 'S']) if gender == 'M' else ''
        )
        ContactInfo.objects.create(
            content_type=ContentType.objects.get_for_model(Student),
            object_id=student.id,
            contact_type='M',
            value=f'+989{randint(10000000, 99999999)}'
        )
        ContactInfo.objects.create(
            content_type=ContentType.objects.get_for_model(Student),
            object_id=student.id,
            contact_type='E',
            value=f'student{i+1}@university.ac.ir'
        )
        students.append(student)

    # ایجاد دروس
    courses = list(Course.objects.all())
    existing_codes = set(course.code for course in courses)
    for i in range(70 - len(courses)):
        code = f'C{i+1:03d}'
        if code not in existing_codes:
            course = Course.objects.create(
                name=f'درس {i+1}',
                code=code,
                credits=randint(1, 4),
                major=choice(majors),
                term=choice(terms)
            )
            courses.append(course)
            existing_codes.add(code)

    # ایجاد کلاس‌ها (با زمان‌بندی بدون تداخل)
    classes = list(Class.objects.all())
    time_slots = [
        (time(8, 0), time(10, 0)),
        (time(10, 0), time(12, 0)),
        (time(13, 0), time(15, 0)),
        (time(15, 0), time(17, 0)),
    ]
    days = ['شنبه', 'یک‌شنبه', 'دوشنبه', 'سه‌شنبه', 'چهارشنبه']
    used_slots = {}

    for i in range(80 - len(classes)):
        course = choice(courses)
        room = choice(rooms)
        day = choice(days)
        start_time, end_time = choice(time_slots)

        slot_key = (room.id, day, start_time, end_time)
        while slot_key in used_slots:
            day = choice(days)
            start_time, end_time = choice(time_slots)
            slot_key = (room.id, day, start_time, end_time)

        used_slots[slot_key] = True

        class_instance = Class.objects.create(
            course=course,
            room=room,
            start_time=start_time,
            end_time=end_time,
            day_of_week=day
        )
        CourseAssignment.objects.create(
            professor=choice(professors),
            class_instance=class_instance
        )
        classes.append(class_instance)

    # ثبت‌نام دانشجویان و تعیین وضعیت فارغ‌التحصیلی
    for student in students:
        num_enrollments = randint(1, 10)
        selected_classes = np.random.choice(classes, size=min(num_enrollments, len(classes)), replace=False)
        
        total_credits = 0
        for class_instance in selected_classes:
            # جلوگیری از ثبت‌نام تکراری
            if not Enrollment.objects.filter(student=student, class_instance=class_instance).exists():
                grade = uniform(0, 20) if randint(0, 1) else None
                status = 'P' if grade and grade >= 10 else ('F' if grade else 'R')
                if status == 'P':
                    total_credits += class_instance.course.credits
                
                Enrollment.objects.create(
                    student=student,
                    class_instance=class_instance,
                    grade=grade,
                    status=status
                )
        
        # تعیین فارغ‌التحصیلی
        if total_credits >= 140:
            student.marital_status = 'S'  # نشانه فارغ‌التحصیلی
            student.save()

if __name__ == '__main__':
    generate_sample_data()