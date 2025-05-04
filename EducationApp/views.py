from django.shortcuts import render

def welcome(request):
    """
    نمایش صفحه خوش‌آمدگویی
    """
    return render(request, 'EducationApp/welcome.html')