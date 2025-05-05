# سیستم آموزش دانشگاهی

این پروژه یک سیستم جامع مدیریت آموزش دانشگاهی است که با استفاده از Django و Django REST Framework پیاده‌سازی شده است.

## قابلیت‌ها

- مدیریت دانشکده‌ها، رشته‌ها، دروس
- مدیریت اساتید و دانشجویان
- ثبت‌نام دانشجویان در کلاس‌ها
- مدیریت ترم‌های تحصیلی
- برنامه‌ریزی کلاس‌ها و زمان‌بندی
- ثبت نمرات و کارنامه دانشجویان

## نصب و راه‌اندازی

1. کلون کردن مخزن:
```bash
git clone https://github.com/Sepahkar/Education.git
cd Education
```

2. ایجاد محیط مجازی:
```bash
python -m venv venv
.\venv\Scripts\activate  # در ویندوز
source venv/bin/activate  # در لینوکس
```

3. نصب وابستگی‌ها:
```bash
pip install -r requirements.txt
```

4. اجرای مهاجرت‌ها:
```bash
python manage.py migrate
```

5. ایجاد داده‌های نمونه:
```bash
python manage.py generate_sample_data
```

6. ایجاد کاربر ادمین:
```bash
python manage.py createsuperuser
```

7. اجرای سرور:
```bash
python manage.py runserver
```

## ساختار پروژه

- `Config/`: تنظیمات اصلی پروژه
- `EducationApp/`: اپلیکیشن اصلی سیستم آموزشی
- `static/`: فایل‌های استاتیک (CSS, JS, تصاویر)
- `templates/`: قالب‌های HTML 