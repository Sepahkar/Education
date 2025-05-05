# ساخت محیط مجازی
python -m venv venv

# فعال‌سازی محیط مجازی
.\venv\Scripts\activate

# ساخت فایل requirements.txt و افزودن نیازمندی‌ها
Set-Content requirements.txt "django"
Add-Content requirements.txt "djangorestframework"

# نصب نیازمندی‌ها
pip install -r requirements.txt

# ساخت پروژه Django
django-admin startproject config .

# ساخت فولدر .vscode و فایل launch.json
New-Item -ItemType Directory -Force -Path .vscode
Set-Content .vscode\launch.json @'
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Django: Runserver",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}\\manage.py",
            "args": [
                "runserver",
                "127.0.0.1:8000"
            ],
            "django": true,
            "justMyCode": true,
            "console": "integratedTerminal",
            "internalConsoleOptions": "neverOpen"
        }
    ]
}
'@

# ساخت اپلیکیشن
python manage.py startapp EducationApp

# ساخت فایل‌های مورد نیاز در EducationApp
$files = @("urls.py", "api.py", "test.py")
foreach ($file in $files) {
    if (-not (Test-Path "EducationApp\$file")) {
        New-Item -ItemType File -Path "EducationApp\$file"
    }
}

# ساخت فولدر static و template
New-Item -ItemType Directory -Force -Path static\EducationApp\css
New-Item -ItemType Directory -Force -Path static\EducationApp\jquery
New-Item -ItemType Directory -Force -Path static\EducationApp\Images
New-Item -ItemType Directory -Force -Path templates\EducationApp

# ساخت فایل‌های استاتیک و تمپلیت
New-Item -ItemType File -Path static\EducationApp\css\education_app.css
New-Item -ItemType File -Path static\EducationApp\jquery\education_app.js
New-Item -ItemType File -Path templates\EducationApp\welcome.html

# افزودن EducationApp و rest_framework به INSTALLED_APPS و تنظیمات static و template
$settingsPath = "config\settings.py"
(Get-Content $settingsPath) -replace "INSTALLED_APPS = \[", "INSTALLED_APPS = [`r`n    'rest_framework',`r`n    'EducationApp'," | Set-Content $settingsPath

# افزودن تنظیمات static و template
Add-Content $settingsPath "`nSTATIC_URL = '/static/'"
Add-Content $settingsPath "STATICFILES_DIRS = [BASE_DIR / 'static']"
Add-Content $settingsPath "TEMPLATES[0]['DIRS'] = [BASE_DIR / 'templates']"

# اطمینان از تنظیم دیتابیس
(Get-Content $settingsPath) -replace "'NAME': BASE_DIR / 'db.sqlite3'", "'NAME': BASE_DIR / 'db.sqlite3'" | Set-Content $settingsPath

# افزودن url اپ به config/urls.py
$urlsPath = "config\urls.py"
$urlsContent = Get-Content $urlsPath
$urlsContent = $urlsContent -replace "from django.urls import path", "from django.urls import path, include"
$urlsContent = $urlsContent -replace "urlpatterns = \[", "urlpatterns = [`r`n    path('EducationApp/', include('EducationApp.urls')),"
Set-Content $urlsPath $urlsContent

# افزودن view به EducationApp/views.py
Set-Content EducationApp\views.py @"
from django.shortcuts import render

def welcome(request):
    return render(request, 'EducationApp/welcome.html')
"@

# افزودن url به EducationApp/urls.py
Set-Content EducationApp\urls.py @"
from django.urls import path
from .views import welcome

urlpatterns = [
    path('', welcome, name='welcome'),
]
"@

# افزودن welcome.html
Set-Content templates\EducationApp\welcome.html @"
<!DOCTYPE html>
<html lang='fa'>
<head>
    <meta charset='UTF-8'>
    <title>سیستم آموزش دانشگاهی</title>
    <link rel='stylesheet' href='/static/EducationApp/css/education_app.css'>
</head>
<body>
    <div class='welcome-container'>
        <img src='/static/EducationApp/Images/university.png' alt='University' style='width:100px;'>
        <h1>به سیستم آموزش دانشگاهی خوش آمدید</h1>
        <p>این پروژه جهت مدیریت امور آموزشی دانشگاه طراحی شده است.</p>
    </div>
    <script src='/static/EducationApp/jquery/education_app.js'></script>
</body>
</html>
"@

# افزودن css
Set-Content static\EducationApp\css\education_app.css @"
.welcome-container {
    font-family: Tahoma, 'Vazir', 'Zar', sans-serif;
    text-align: center;
    margin-top: 50px;
}
"@

# اجرای migrate برای ساخت db.sqlite3
python manage.py migrate

Write-Host "پروژه با موفقیت ساخته شد. برای اجرا کلید F5 را در VSCode بزنید یا دستور python manage.py runserver را اجرا کنید."