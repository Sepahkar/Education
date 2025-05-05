import random
import string
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from EducationApp.models import (
    Faculty, Department, Professor, Student, Semester, Room, Course, 
    ClassOffering, ClassSession, Enrollment, ContactInfo,
    GENDER_CHOICES, MARITAL_STATUS_CHOICES, MILITARY_STATUS_CHOICES,
    PROFESSOR_CONTRACT_CHOICES, STUDENT_STATUS_CHOICES, CONTACT_TYPE_CHOICES,
    WEEKDAY_CHOICES
)

# فهرست نام‌های پسرانه
MALE_FIRST_NAMES = [
    'علی', 'محمد', 'امیر', 'حسین', 'احمد', 'محمدرضا', 'مهدی', 'سعید', 'رضا', 'امیرحسین',
    'محسن', 'فرهاد', 'مجتبی', 'بهزاد', 'داود', 'سینا', 'پوریا', 'محمدعلی', 'جواد', 'پیمان',
    'بهرام', 'عباس', 'ابراهیم', 'مصطفی', 'یاسر', 'کیوان', 'حامد', 'فرزاد', 'بهنام', 'هادی',
    'وحید', 'حمید', 'اکبر', 'میلاد', 'کامران', 'پدرام', 'پژمان', 'مرتضی', 'شهرام', 'نیما',
    'مهران', 'سامان', 'امید', 'صادق', 'محمدمهدی', 'کاوه', 'پارسا', 'حسن', 'علیرضا', 'سهراب'
]

# فهرست نام‌های دخترانه
FEMALE_FIRST_NAMES = [
    'فاطمه', 'زهرا', 'مریم', 'سارا', 'نرگس', 'لیلا', 'الهام', 'الهه', 'زهره', 'سمیرا',
    'نازنین', 'مهسا', 'نیلوفر', 'صبا', 'پریسا', 'مینا', 'ترانه', 'آزاده', 'زینب', 'مبینا',
    'شیوا', 'سمانه', 'یاسمن', 'مهناز', 'لادن', 'شیرین', 'نسترن', 'فرزانه', 'هانیه', 'شقایق',
    'فرناز', 'سپیده', 'رویا', 'سمیه', 'رعنا', 'فریبا', 'مهتاب', 'نگار', 'پریناز', 'راضیه',
    'آتنا', 'فروغ', 'شیدا', 'مونا', 'ندا', 'لیدا', 'شهرزاد', 'آرزو', 'پگاه', 'مژده'
]

# فهرست نام‌های خانوادگی
LAST_NAMES = [
    'محمدی', 'احمدی', 'رضایی', 'حسینی', 'موسوی', 'علیزاده', 'نجفی', 'صادقی', 'صالحی', 'کریمی',
    'میرزایی', 'اکبری', 'یوسفی', 'هاشمی', 'قاسمی', 'طاهری', 'جعفری', 'حیدری', 'محمودی', 'فرهادی',
    'نوری', 'قربانی', 'رحیمی', 'مرادی', 'سلیمانی', 'عباسی', 'ابراهیمی', 'رحمانی', 'فتحی', 'جلالی',
    'کاظمی', 'عزیزی', 'امینی', 'رضوی', 'قدیری', 'فراهانی', 'زارعی', 'اسدی', 'عظیمی', 'شریفی',
    'بهرامی', 'امیری', 'باقری', 'معینی', 'شفیعی', 'شیرازی', 'نظری', 'خلیلی', 'جمالی', 'حسنی',
    'حقیقی', 'دانشور', 'دهقانی', 'رستمی', 'زمانی', 'سجادی', 'سعیدی', 'شکوهی', 'صابری', 'صمدی',
    'طباطبایی', 'عابدی', 'غفاری', 'فخاری', 'فرزانه', 'قادری', 'قنبری', 'کمالی', 'محبی', 'منصوری',
    'مهدوی', 'نادری', 'نعمتی', 'هدایتی', 'وکیلی', 'یزدانی', 'صالحیان', 'پناهی', 'جلیلی', 'داوودی'
]

# فهرست شهرهای ایران
IRANIAN_CITIES = [
    'تهران', 'مشهد', 'اصفهان', 'کرج', 'شیراز', 'تبریز', 'قم', 'اهواز', 'کرمانشاه', 'ارومیه',
    'رشت', 'زاهدان', 'همدان', 'کرمان', 'یزد', 'اردبیل', 'بندرعباس', 'اراک', 'زنجان', 'ساری',
    'قزوین', 'سنندج', 'خرم‌آباد', 'گرگان', 'بیرجند', 'بجنورد', 'ایلام', 'شهرکرد', 'سمنان', 'یاسوج'
]

# آدرس‌های محله‌های تهران
TEHRAN_ADDRESSES = [
    'تهران، میدان ونک، خیابان ملاصدرا، پلاک ۱۲، واحد ۴',
    'تهران، جردن، خیابان گلشهر، کوچه دوم، پلاک ۸',
    'تهران، نیاوران، خیابان پورابتهاج، پلاک ۲۳',
    'تهران، پاسداران، خیابان گلستان پنجم، پلاک ۱۵، طبقه ۳',
    'تهران، سعادت‌آباد، میدان کاج، خیابان سرو غربی، پلاک ۴۷',
    'تهران، تجریش، خیابان مقصودبیک، کوچه حافظ، پلاک ۹',
    'تهران، ولنجک، بلوار دانشجو، خیابان عدالت، پلاک ۳۲',
    'تهران، ظفر، خیابان فرید افشار، کوچه آذر، پلاک ۱۹',
    'تهران، امیرآباد، خیابان شانزدهم، پلاک ۵، واحد ۷',
    'تهران، بلوار میرداماد، خیابان البرز، پلاک ۷۸، واحد ۱۲',
    'تهران، پونک، بلوار عدل، کوچه شقایق، پلاک ۹۰',
    'تهران، یوسف‌آباد، خیابان سید جمال‌الدین اسدآبادی، کوچه ۳۵، پلاک ۶',
    'تهران، جمهوری، خیابان ملت، کوچه شاهرود، پلاک ۲۱',
    'تهران، پیروزی، خیابان پنجم نیرو هوایی، کوچه یکم، پلاک ۱۵',
    'تهران، نارمک، خیابان گلبرگ، کوچه سیاوش، پلاک ۴۳',
    'تهران، تهرانپارس، خیابان احسان، کوچه پنجم غربی، پلاک ۱۰۷',
    'تهران، شهرک غرب، بلوار دادمان، خیابان درختی، پلاک ۶۳',
    'تهران، صادقیه، بلوار آیت‌الله کاشانی، کوچه بهار، پلاک ۳۷',
    'تهران، آریاشهر، بلوار فردوس، خیابان وفا آذر، پلاک ۸۸',
    'تهران، مرزداران، خیابان سرسبز، کوچه لاله، پلاک ۲۷'
]

# نام دانشکده‌ها
FACULTY_NAMES = [
    'دانشکده علوم',
    'دانشکده فنی و مهندسی',
    'دانشکده علوم انسانی',
    'دانشکده پزشکی',
    'دانشکده هنر و معماری',
    'دانشکده ادبیات',
    'دانشکده اقتصاد و مدیریت',
    'دانشکده کشاورزی',
    'دانشکده حقوق',
    'دانشکده علوم رایانه'
]

# نام رشته‌های تحصیلی
DEPARTMENT_NAMES = {
    'دانشکده علوم': [
        'فیزیک', 'شیمی', 'زیست‌شناسی', 'ریاضیات'
    ],
    'دانشکده فنی و مهندسی': [
        'مهندسی برق', 'مهندسی عمران', 'مهندسی مکانیک', 'مهندسی نفت', 'مهندسی صنایع'
    ],
    'دانشکده علوم انسانی': [
        'روانشناسی', 'علوم تربیتی', 'جامعه‌شناسی'
    ],
    'دانشکده پزشکی': [
        'پزشکی', 'داروسازی', 'دندانپزشکی', 'پرستاری'
    ],
    'دانشکده هنر و معماری': [
        'معماری', 'گرافیک', 'نقاشی', 'موسیقی'
    ],
    'دانشکده ادبیات': [
        'زبان و ادبیات فارسی', 'زبان و ادبیات انگلیسی', 'مترجمی زبان'
    ],
    'دانشکده اقتصاد و مدیریت': [
        'حسابداری', 'مدیریت بازرگانی', 'اقتصاد'
    ],
    'دانشکده کشاورزی': [
        'علوم خاک', 'گیاه‌پزشکی', 'باغبانی'
    ],
    'دانشکده حقوق': [
        'حقوق', 'علوم سیاسی'
    ],
    'دانشکده علوم رایانه': [
        'مهندسی کامپیوتر', 'علوم کامپیوتر', 'فناوری اطلاعات'
    ]
}

# رتبه‌های علمی اساتید
ACADEMIC_RANKS = ['استاد', 'دانشیار', 'استادیار', 'مربی']

# مدارک تحصیلی
EDUCATION_LEVELS = ['دکتری', 'کارشناسی ارشد', 'کارشناسی']

# تولید کد ملی معتبر به صورت تصادفی
def generate_valid_national_code():
    # ۹ رقم اول تصادفی
    digits = [random.randint(0, 9) for _ in range(9)]
    
    # محاسبه رقم کنترلی (رقم آخر)
    weighted_sum = sum((10 - i) * digit for i, digit in enumerate(digits))
    remainder = weighted_sum % 11
    control_digit = remainder if remainder < 2 else 11 - remainder
    
    # ترکیب همه اعداد در یک رشته
    national_code = ''.join(map(str, digits)) + str(control_digit)
    return national_code

# تابع کمکی برای تولید شماره دانشجویی و کد استادی
def generate_unique_code(prefix, year, sequence, total_length=10):
    year_part = str(year)[-2:]  # فقط ۲ رقم آخر سال
    sequence_str = str(sequence).zfill(total_length - len(prefix) - len(year_part))
    return f"{prefix}{year_part}{sequence_str}"

class Command(BaseCommand):
    help = 'Generates sample data for the education system'

    def handle(self, *args, **options):
        self.stdout.write('Starting data generation process...')
        
        self.create_faculties()
        self.create_departments()
        self.create_professors()
        self.create_students()
        self.create_semesters()
        self.create_rooms()
        self.create_courses()
        self.create_class_offerings()
        self.create_enrollments()
        
        self.stdout.write(self.style.SUCCESS('Sample data generation completed successfully!'))
    
    def create_faculties(self):
        self.stdout.write('Creating faculties...')
        for i, name in enumerate(FACULTY_NAMES):
            faculty = Faculty.objects.create(
                code=f'F{str(i+1).zfill(2)}',
                name=name,
                establishment_date=timezone.now().date() - timedelta(days=random.randint(365*10, 365*30)),
                address=random.choice(TEHRAN_ADDRESSES),
                description=f'توضیحات مربوط به {name}'
            )
        
        self.stdout.write(self.style.SUCCESS(f'Created {len(FACULTY_NAMES)} faculties'))
    
    def create_departments(self):
        self.stdout.write('Creating departments...')
        faculties = Faculty.objects.all()
        
        dept_count = 0
        for faculty in faculties:
            dept_names = DEPARTMENT_NAMES.get(faculty.name, [])
            for i, name in enumerate(dept_names):
                dept_count += 1
                Department.objects.create(
                    code=f'D{str(dept_count).zfill(3)}',
                    name=name,
                    faculty=faculty,
                    establishment_date=faculty.establishment_date + timedelta(days=random.randint(0, 365*5)),
                    total_credits=random.choice([120, 140, 180]),
                    description=f'توضیحات مربوط به رشته {name} در {faculty.name}'
                )
        
        self.stdout.write(self.style.SUCCESS(f'Created {dept_count} departments'))
    
    def create_professors(self):
        self.stdout.write('Creating professors...')
        departments = Department.objects.all()
        
        for i in range(100):
            gender = random.choice(['M', 'F'])
            first_name = random.choice(MALE_FIRST_NAMES if gender == 'M' else FEMALE_FIRST_NAMES)
            last_name = random.choice(LAST_NAMES)
            
            professor = Professor.objects.create(
                first_name=first_name,
                last_name=last_name,
                national_code=generate_valid_national_code(),
                birth_certificate_number=str(random.randint(10000000, 99999999)),
                birth_date=timezone.now().date() - timedelta(days=random.randint(365*30, 365*70)),
                birth_place=random.choice(IRANIAN_CITIES),
                gender=gender,
                marital_status=random.choice(['S', 'M']),
                address=random.choice(TEHRAN_ADDRESSES),
                professor_code=generate_unique_code('P', random.randint(1390, 1403), i+1),
                department=random.choice(departments),
                academic_rank=random.choice(ACADEMIC_RANKS),
                contract_type=random.choice(['FT', 'PT', 'I']),
                employment_date=timezone.now().date() - timedelta(days=random.randint(365*1, 365*20)),
                education_level=random.choice(EDUCATION_LEVELS),
                specialization=f'تخصص در {random.choice(["فیزیک کوانتوم", "هوش مصنوعی", "ادبیات تطبیقی", "مدیریت استراتژیک", "مهندسی نرم‌افزار"])}'
            )
            
            # افزودن اطلاعات تماس
            content_type = ContentType.objects.get_for_model(Professor)
            
            # شماره موبایل
            mobile = f'09{random.randint(10, 99)}{random.randint(1000000, 9999999)}'
            ContactInfo.objects.create(
                content_type=content_type,
                object_id=professor.id,
                contact_type='M',
                value=mobile,
                is_primary=True
            )
            
            # آدرس ایمیل
            email = f'{first_name.lower()}.{last_name.lower()}{random.randint(100, 999)}@university.ac.ir'
            ContactInfo.objects.create(
                content_type=content_type,
                object_id=professor.id,
                contact_type='O',
                value=email,
                is_primary=True
            )
        
        self.stdout.write(self.style.SUCCESS('Created 100 professors'))
    
    def create_students(self):
        self.stdout.write('Creating students...')
        departments = Department.objects.all()
        
        # وضعیت دانشجویان (با توزیع مناسب)
        status_weights = {
            'AC': 65,  # فعال
            'ON': 10,  # مرخصی
            'GR': 20,  # فارغ‌التحصیل
            'EX': 2,   # اخراج
            'WT': 3    # انصراف
        }
        status_choices = []
        for status, weight in status_weights.items():
            status_choices.extend([status] * weight)
        
        for i in range(1000):
            gender = random.choice(['M', 'F'])
            first_name = random.choice(MALE_FIRST_NAMES if gender == 'M' else FEMALE_FIRST_NAMES)
            last_name = random.choice(LAST_NAMES)
            admission_year = random.randint(1398, 1403)
            admission_date = timezone.datetime(admission_year, 9, 1).date()
            
            student_status = random.choice(status_choices)
            graduation_date = None
            if student_status == 'GR':
                graduation_year = admission_year + random.randint(3, 6)
                if graduation_year <= 1403:  # سال فعلی
                    graduation_date = timezone.datetime(graduation_year, 6, 30).date()
                else:
                    graduation_date = None
                    student_status = 'AC'  # تغییر به فعال اگر هنوز فارغ‌التحصیل نشده است
            
            student = Student.objects.create(
                first_name=first_name,
                last_name=last_name,
                national_code=generate_valid_national_code(),
                birth_certificate_number=str(random.randint(10000000, 99999999)),
                birth_date=timezone.now().date() - timedelta(days=random.randint(365*18, 365*35)),
                birth_place=random.choice(IRANIAN_CITIES),
                gender=gender,
                marital_status=random.choice(['S', 'M']),
                address=random.choice(TEHRAN_ADDRESSES),
                student_code=generate_unique_code('S', admission_year, i+1),
                department=random.choice(departments),
                admission_date=admission_date,
                military_status=random.choice(['S', 'E', 'F', 'P', 'N']) if gender == 'M' else None,
                student_status=student_status,
                graduation_date=graduation_date
            )
            
            # افزودن اطلاعات تماس
            content_type = ContentType.objects.get_for_model(Student)
            
            # شماره موبایل
            mobile = f'09{random.randint(10, 99)}{random.randint(1000000, 9999999)}'
            ContactInfo.objects.create(
                content_type=content_type,
                object_id=student.id,
                contact_type='M',
                value=mobile,
                is_primary=True
            )
            
            # آدرس ایمیل
            email = f'{first_name.lower()}.{last_name.lower()}{random.randint(100, 999)}@student.university.ac.ir'
            ContactInfo.objects.create(
                content_type=content_type,
                object_id=student.id,
                contact_type='O',
                value=email,
                is_primary=True
            )
        
        self.stdout.write(self.style.SUCCESS('Created 1000 students'))
    
    def create_semesters(self):
        self.stdout.write('Creating semesters...')
        
        # ترم‌های پاییز و بهار از سال ۱۳۹۸ تا ۱۴۰۳
        for year in range(1398, 1404):
            # ترم پاییز
            fall_start = timezone.datetime(year, 9, 1).date()
            fall_end = timezone.datetime(year, 1, 30).date()
            Semester.objects.create(
                academic_year=year,
                semester_type='F',
                start_date=fall_start,
                end_date=fall_end,
                is_active=(year == 1403 and timezone.now().date() > fall_start and timezone.now().date() < fall_end)
            )
            
            # ترم بهار
            spring_start = timezone.datetime(year, 2, 15).date()
            spring_end = timezone.datetime(year, 6, 30).date()
            Semester.objects.create(
                academic_year=year,
                semester_type='S',
                start_date=spring_start,
                end_date=spring_end,
                is_active=(year == 1403 and timezone.now().date() > spring_start and timezone.now().date() < spring_end)
            )
        
        self.stdout.write(self.style.SUCCESS('Created 12 semesters (1398-1403)'))
    
    def create_rooms(self):
        self.stdout.write('Creating rooms...')
        faculties = Faculty.objects.all()
        
        for faculty in faculties:
            num_rooms = random.randint(5, 15)
            used_room_numbers = set()  # مجموعه شماره اتاق‌های استفاده شده
            
            for i in range(num_rooms):
                # ایجاد شماره اتاق منحصر به فرد
                while True:
                    floor = random.randint(1, 5)
                    room_num = random.randint(1, 20)
                    room_number = f"{floor}{room_num:02d}"
                    
                    if room_number not in used_room_numbers:
                        used_room_numbers.add(room_number)
                        break
                
                Room.objects.create(
                    room_number=room_number,
                    faculty=faculty,
                    capacity=random.choice([20, 30, 40, 50, 70, 100]),
                    has_projector=random.choice([True, False]),
                    floor=floor,
                    description=f"اتاق {room_number} در طبقه {floor} از ساختمان {faculty.name}"
                )
        
        self.stdout.write(self.style.SUCCESS(f'Created {Room.objects.count()} rooms'))
    
    def create_courses(self):
        self.stdout.write('Creating courses...')
        departments = Department.objects.all()
        
        course_titles = {
            'فیزیک': ['فیزیک پایه ۱', 'فیزیک پایه ۲', 'مکانیک کوانتومی', 'الکترومغناطیس'],
            'شیمی': ['شیمی آلی', 'شیمی معدنی', 'شیمی تجزیه', 'شیمی فیزیک'],
            'زیست‌شناسی': ['سلول‌شناسی', 'ژنتیک', 'بیوشیمی', 'میکروبیولوژی'],
            'ریاضیات': ['ریاضی ۱', 'ریاضی ۲', 'معادلات دیفرانسیل', 'آنالیز عددی'],
            'مهندسی برق': ['مدارهای الکتریکی', 'الکترونیک ۱', 'الکترونیک ۲', 'سیستم‌های کنترل'],
            'مهندسی عمران': ['استاتیک', 'مقاومت مصالح', 'هیدرولیک', 'سازه‌های بتنی'],
            'مهندسی مکانیک': ['ترمودینامیک', 'مکانیک سیالات', 'مقاومت مصالح', 'طراحی اجزا'],
            'مهندسی کامپیوتر': ['برنامه‌نویسی پیشرفته', 'ساختمان داده‌ها', 'هوش مصنوعی', 'پایگاه داده‌ها', 'شبکه‌های کامپیوتری'],
            'حقوق': ['حقوق مدنی', 'حقوق تجارت', 'حقوق اساسی', 'آیین دادرسی مدنی'],
            'مدیریت بازرگانی': ['اصول مدیریت', 'مدیریت منابع انسانی', 'بازاریابی', 'مدیریت مالی']
        }
        
        course_count = 0
        for department in departments:
            base_titles = course_titles.get(department.name, [])
            if not base_titles:
                general_titles = ['ریاضی ۱', 'فیزیک ۱', 'زبان تخصصی', 'روش تحقیق']
                base_titles = [f"{department.name} {i+1}" for i in range(3)] + general_titles
            
            num_courses = min(len(base_titles) + 2, 7)
            for i in range(num_courses):
                if i < len(base_titles):
                    title = base_titles[i]
                else:
                    title = f"درس اختیاری {department.name} {i-len(base_titles)+1}"
                
                course_count += 1
                Course.objects.create(
                    course_code=f'C{str(course_count).zfill(3)}',
                    title=title,
                    department=department,
                    credits=random.choice([1, 2, 3, 4]),
                    is_practical=random.choice([True, False]),
                    description=f"توضیحات مربوط به درس {title} در رشته {department.name}"
                )
        
        # ایجاد پیش‌نیازها
        courses = Course.objects.all()
        for course in courses:
            # برای برخی دروس، دروس دیگر همان رشته را به عنوان پیش‌نیاز قرار می‌دهیم
            if random.random() < 0.4:  # 40% احتمال داشتن پیش‌نیاز
                department_courses = Course.objects.filter(department=course.department).exclude(id=course.id)
                prerequisites = list(department_courses)
                random.shuffle(prerequisites)
                
                # انتخاب تعدادی از دروس هم‌رشته به عنوان پیش‌نیاز
                num_prerequisites = min(random.randint(0, 2), len(prerequisites))
                for i in range(num_prerequisites):
                    course.prerequisites.add(prerequisites[i])
        
        self.stdout.write(self.style.SUCCESS(f'Created {course_count} courses'))
    
    def create_class_offerings(self):
        self.stdout.write('Creating class offerings...')
        courses = Course.objects.all()
        professors = Professor.objects.all()
        semesters = Semester.objects.all()
        rooms = Room.objects.all()
        
        # ساختار برای نگهداری اطلاعات جلسات کلاس‌ها
        # {(room_id, weekday, start_time, end_time): True}
        reserved_sessions = {}
        
        class_count = 0
        for semester in semesters:
            # نسبت دروس ارائه شده در هر ترم حدود 40 تا 60 درس
            semester_courses = random.sample(list(courses), min(random.randint(40, 60), courses.count()))
            
            for course in semester_courses:
                # ممکن است برای یک درس چند گروه ارائه شود
                num_groups = random.randint(1, 2)
                
                for group in range(1, num_groups + 1):
                    class_count += 1
                    capacity = random.randint(15, 40)
                    
                    # انتخاب استاد مناسب (ترجیحاً از همان دپارتمان)
                    department_professors = professors.filter(department=course.department)
                    if department_professors.exists():
                        professor = random.choice(department_professors)
                    else:
                        professor = random.choice(professors)
                    
                    class_offering = ClassOffering.objects.create(
                        course=course,
                        semester=semester,
                        professor=professor,
                        class_code=f"{course.course_code}-{group}",
                        capacity=capacity
                    )
                    
                    # ایجاد جلسات کلاس
                    # تعداد جلسات براساس تعداد واحد
                    num_sessions = 1 if course.credits <= 2 else 2
                    
                    # انتخاب اتاق مناسب (ترجیحاً در دانشکده مربوطه)
                    faculty_rooms = rooms.filter(faculty=course.department.faculty)
                    if not faculty_rooms.exists():
                        faculty_rooms = rooms
                    
                    room = random.choice(faculty_rooms)
                    
                    # روزهای هفته برای کلاس
                    weekdays = random.sample(range(5), min(num_sessions, 5))  # 0-4 (شنبه تا چهارشنبه)
                    
                    sessions_created = 0
                    max_attempts = 10  # حداکثر تلاش برای ایجاد جلسه کلاس
                    
                    while sessions_created < num_sessions and max_attempts > 0:
                        weekday = random.choice(range(5))  # برای تنوع بیشتر
                        
                        # زمان‌های کلاس
                        start_hour = random.choice([8, 10, 13, 15])
                        duration = 1.5 if course.credits <= 2 else 2
                        
                        start_time = f"{start_hour}:00"
                        end_hour = start_hour + int(duration)
                        end_minute = '30' if duration % 1 == 0.5 else '00'
                        end_time = f"{end_hour}:{end_minute}"
                        
                        # بررسی تداخل زمانی
                        session_key = (room.id, weekday, start_time, end_time)
                        
                        # اگر این زمان قبلاً رزرو نشده باشد
                        if session_key not in reserved_sessions:
                            try:
                                ClassSession.objects.create(
                                    class_offering=class_offering,
                                    room=room,
                                    weekday=weekday,
                                    start_time=start_time,
                                    end_time=end_time
                                )
                                # علامت‌گذاری این زمان به عنوان رزرو شده
                                reserved_sessions[session_key] = True
                                sessions_created += 1
                            except Exception as e:
                                max_attempts -= 1
                        else:
                            max_attempts -= 1
        
        self.stdout.write(self.style.SUCCESS(f'Created {class_count} class offerings with {ClassSession.objects.count()} sessions'))
    
    def create_enrollments(self):
        self.stdout.write('Creating enrollments...')
        students = Student.objects.filter(student_status__in=['AC', 'GR'])
        class_offerings = ClassOffering.objects.all()
        
        enrollment_count = 0
        for student in students:
            # تعیین ترم‌هایی که دانشجو در آنها ثبت‌نام کرده است
            student_semesters = []
            
            # ترم‌های بعد از تاریخ پذیرش
            eligible_semesters = Semester.objects.filter(start_date__gte=student.admission_date)
            
            # اگر دانشجو فارغ‌التحصیل شده، ترم‌های بعد از تاریخ فارغ‌التحصیلی را حذف می‌کنیم
            if student.graduation_date:
                eligible_semesters = eligible_semesters.filter(end_date__lte=student.graduation_date)
            
            # تعداد ترم‌های ثبت‌نامی (با احتمال مرخصی)
            num_semesters = min(eligible_semesters.count(), random.randint(1, 8))
            student_semesters = list(eligible_semesters)[:num_semesters]
            
            for semester in student_semesters:
                # تعداد دروس انتخاب شده در هر ترم
                num_courses = random.randint(3, 6)
                
                # دروس ارائه شده در این ترم
                semester_classes = list(class_offerings.filter(semester=semester))
                random.shuffle(semester_classes)
                
                # انتخاب تعدادی درس برای ثبت‌نام
                for i in range(min(num_courses, len(semester_classes))):
                    class_offering = semester_classes[i]
                    
                    # وضعیت ثبت‌نام
                    status = random.choice(['A'] * 9 + ['D'])  # 90% تایید شده، 10% حذف شده
                    
                    # نمره (برای ترم‌های گذشته)
                    grade = None
                    if semester.end_date < timezone.now().date() and status == 'A':
                        grade = round(random.uniform(0, 20), 2)
                    
                    enrollment_count += 1
                    Enrollment.objects.create(
                        student=student,
                        class_offering=class_offering,
                        status=status,
                        grade=grade
                    )
        
        self.stdout.write(self.style.SUCCESS(f'Created {enrollment_count} enrollments')) 