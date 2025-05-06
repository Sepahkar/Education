from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Customer, InsuranceCompany, InsuranceType, Coverage, Policy, Annex
from datetime import timedelta
import json

# Create your views here.

# Basic views
def home(request):
    """صفحه اصلی سیستم بیمه"""
    companies = InsuranceCompany.objects.filter(is_active=True)
    insurance_types = InsuranceType.objects.filter(is_active=True)
    
    context = {
        'companies': companies,
        'insurance_types': insurance_types,
    }
    return render(request, 'insurance/home.html', context)

def company_list(request):
    """لیست شرکت‌های بیمه"""
    companies = InsuranceCompany.objects.filter(is_active=True)
    context = {
        'companies': companies,
    }
    return render(request, 'insurance/company_list.html', context)

def insurance_type_list(request):
    """لیست انواع بیمه"""
    insurance_types = InsuranceType.objects.filter(is_active=True)
    context = {
        'insurance_types': insurance_types,
    }
    return render(request, 'insurance/insurance_type_list.html', context)

# Customer views
def customer_login(request):
    """صفحه ورود مشتریان"""
    if request.method == 'POST':
        customer_id = request.POST.get('customer_id')
        password = request.POST.get('password')
        
        try:
            # در یک سیستم واقعی باید از مکانیزم احراز هویت جنگو استفاده شود
            # اینجا فقط برای نمایش، یک بررسی ساده انجام می‌دهیم
            customer = Customer.objects.get(id=customer_id)
            if password == '123456':  # کلمه عبور ثابت برای همه مشتریان
                request.session['customer_id'] = customer.id
                messages.success(request, f'خوش آمدید {customer.full_name}')
                return redirect('insurance:customer_dashboard')
            else:
                messages.error(request, 'کلمه عبور نادرست است')
        except Customer.DoesNotExist:
            messages.error(request, 'شناسه مشتری نامعتبر است')
    
    return render(request, 'insurance/customer_login.html')

def customer_logout(request):
    """خروج مشتری"""
    if 'customer_id' in request.session:
        del request.session['customer_id']
    return redirect('insurance:customer_login')

def customer_dashboard(request):
    """داشبورد مشتری"""
    if 'customer_id' not in request.session:
        messages.warning(request, 'لطفا ابتدا وارد شوید')
        return redirect('insurance:customer_login')
    
    customer = get_object_or_404(Customer, id=request.session['customer_id'])
    active_policies = Policy.objects.filter(customer=customer, status='active')
    expired_policies = Policy.objects.filter(customer=customer, status='expired')
    
    # بیمه‌نامه‌های نزدیک به انقضا (30 روز آینده)
    today = timezone.now().date()
    expiring_soon = active_policies.filter(
        expiry_date__gt=today,
        expiry_date__lte=today + timezone.timedelta(days=30)
    )
    
    context = {
        'customer': customer,
        'active_policies_count': active_policies.count(),
        'expired_policies_count': expired_policies.count(),
        'expiring_soon': expiring_soon,
    }
    return render(request, 'insurance/customer_dashboard.html', context)

def customer_policies(request):
    """لیست بیمه‌نامه‌های مشتری"""
    if 'customer_id' not in request.session:
        messages.warning(request, 'لطفا ابتدا وارد شوید')
        return redirect('insurance:customer_login')
    
    customer = get_object_or_404(Customer, id=request.session['customer_id'])
    policies = Policy.objects.filter(customer=customer).order_by('-issue_date')
    
    # فیلتر بیمه‌نامه‌های نزدیک به انقضا (کمتر از 30 روز)
    filter_expiring_soon = request.GET.get('expiring_soon', False)
    
    if filter_expiring_soon:
        today = timezone.now().date()
        policies = policies.filter(
            status='active',
            expiry_date__gt=today,
            expiry_date__lte=today + timezone.timedelta(days=30)
        )
    
    # محاسبه تعداد بیمه‌نامه‌های نزدیک به انقضا
    today = timezone.now().date()
    expiring_soon_count = policies.filter(
        status='active',
        expiry_date__gt=today,
        expiry_date__lte=today + timezone.timedelta(days=30)
    ).count()
    
    context = {
        'customer': customer,
        'policies': policies,
        'filter_expiring_soon': filter_expiring_soon,
        'expiring_soon_count': expiring_soon_count
    }
    return render(request, 'insurance/customer_policies.html', context)

def policy_extend(request, policy_number):
    """تمدید بیمه‌نامه"""
    if 'customer_id' not in request.session:
        messages.warning(request, 'لطفا ابتدا وارد شوید')
        return redirect('insurance:customer_login')
    
    customer = get_object_or_404(Customer, id=request.session['customer_id'])
    policy = get_object_or_404(Policy, policy_number=policy_number, customer=customer)
    
    # بررسی اینکه آیا بیمه‌نامه قابل تمدید است
    today = timezone.now().date()
    
    # اگر بیمه‌نامه منقضی شده و بیش از 30 روز از انقضای آن گذشته باشد
    if policy.is_expired and (today - policy.expiry_date).days > 30:
        messages.error(request, 'این بیمه‌نامه قابل تمدید نیست. بیش از 30 روز از انقضای آن گذشته است.')
        return redirect('insurance:customer_policies')
    
    # تمدید بیمه‌نامه
    if policy.is_expired:
        # اگر منقضی شده، از امروز یک سال تمدید می‌شود
        policy.issue_date = today
        policy.expiry_date = today + timedelta(days=365)
    else:
        # در غیر این صورت، یک سال به تاریخ انقضای فعلی اضافه می‌شود
        policy.expiry_date = policy.expiry_date + timedelta(days=365)
    
    policy.status = 'active'
    policy.save()
    
    messages.success(request, f'بیمه‌نامه {policy.policy_number} با موفقیت تمدید شد.')
    return redirect('insurance:customer_policies')

def policy_detail(request, policy_number):
    """جزئیات بیمه‌نامه"""
    if 'customer_id' not in request.session:
        messages.warning(request, 'لطفا ابتدا وارد شوید')
        return redirect('insurance:customer_login')
    
    customer = get_object_or_404(Customer, id=request.session['customer_id'])
    policy = get_object_or_404(Policy, policy_number=policy_number, customer=customer)
    annexes = Annex.objects.filter(policy=policy).order_by('-issue_date')
    
    context = {
        'customer': customer,
        'policy': policy,
        'annexes': annexes,
    }
    return render(request, 'insurance/policy_detail.html', context)

def add_annex(request, policy_number):
    """افزودن الحاقیه به بیمه‌نامه"""
    if 'customer_id' not in request.session:
        messages.warning(request, 'لطفا ابتدا وارد شوید')
        return redirect('insurance:customer_login')
    
    customer = get_object_or_404(Customer, id=request.session['customer_id'])
    policy = get_object_or_404(Policy, policy_number=policy_number, customer=customer)
    
    # بررسی اینکه بیمه‌نامه فعال باشد
    if policy.status != 'active':
        messages.error(request, 'فقط برای بیمه‌نامه‌های فعال می‌توانید الحاقیه صادر کنید.')
        return redirect('insurance:policy_detail', policy_number=policy_number)
    
    if request.method == 'POST':
        # دریافت داده‌های فرم
        description = request.POST.get('description', '')
        additional_premium = request.POST.get('additional_premium', 0)
        coverages_added_ids = request.POST.getlist('coverages_added', [])
        coverages_removed_ids = request.POST.getlist('coverages_removed', [])
        
        # ایجاد الحاقیه
        annex = Annex.objects.create(
            policy=policy,
            description=description,
            issue_date=timezone.now().date(),
            additional_premium=additional_premium
        )
        
        # اضافه کردن پوشش‌های جدید
        if coverages_added_ids:
            coverages_to_add = Coverage.objects.filter(id__in=coverages_added_ids)
            for coverage in coverages_to_add:
                annex.coverages_added.add(coverage)
                policy.coverages.add(coverage)
        
        # حذف پوشش‌های انتخاب شده
        if coverages_removed_ids:
            coverages_to_remove = Coverage.objects.filter(id__in=coverages_removed_ids)
            for coverage in coverages_to_remove:
                annex.coverages_removed.add(coverage)
                policy.coverages.remove(coverage)
        
        messages.success(request, f'الحاقیه با شماره {annex.annex_number} با موفقیت صادر شد.')
        return redirect('insurance:policy_detail', policy_number=policy_number)
    
    # دریافت پوشش‌های موجود و پوشش‌های قابل اضافه
    current_coverages = policy.coverages.all()
    all_coverages = Coverage.objects.filter(insurance_type=policy.insurance_type, is_active=True)
    available_coverages = [c for c in all_coverages if c not in current_coverages]
    
    context = {
        'customer': customer,
        'policy': policy,
        'current_coverages': current_coverages,
        'available_coverages': available_coverages,
    }
    return render(request, 'insurance/add_annex.html', context)

def customer_profile(request):
    """پروفایل مشتری"""
    if 'customer_id' not in request.session:
        messages.warning(request, 'لطفا ابتدا وارد شوید')
        return redirect('insurance:customer_login')
    
    customer = get_object_or_404(Customer, id=request.session['customer_id'])
    
    if request.method == 'POST':
        # به‌روزرسانی اطلاعات مشتری
        customer.phone_number = request.POST.get('phone_number', customer.phone_number)
        customer.email = request.POST.get('email', customer.email)
        customer.address = request.POST.get('address', customer.address)
        customer.save()
        messages.success(request, 'اطلاعات شما با موفقیت به‌روزرسانی شد')
        return redirect('insurance:customer_profile')
    
    context = {
        'customer': customer,
    }
    return render(request, 'insurance/customer_profile.html', context)

# API views
@api_view(['GET'])
def api_company_list(request):
    """API لیست شرکت‌های بیمه"""
    companies = InsuranceCompany.objects.filter(is_active=True)
    data = [{
        'id': company.id,
        'name': company.name,
        'code': company.code,
        'logo_url': company.logo_url,
        'website': company.website,
    } for company in companies]
    return Response(data)

@api_view(['GET'])
def api_insurance_type_list(request):
    """API لیست انواع بیمه"""
    insurance_types = InsuranceType.objects.filter(is_active=True)
    data = [{
        'id': ins_type.id,
        'name': ins_type.name,
        'code': ins_type.code,
        'description': ins_type.description,
    } for ins_type in insurance_types]
    return Response(data)

@api_view(['GET'])
def api_coverage_list(request):
    """API لیست پوشش‌های بیمه"""
    insurance_type_id = request.query_params.get('insurance_type_id', None)
    
    if insurance_type_id:
        coverages = Coverage.objects.filter(insurance_type_id=insurance_type_id, is_active=True)
    else:
        coverages = Coverage.objects.filter(is_active=True)
    
    data = [{
        'id': coverage.id,
        'name': coverage.name,
        'code': coverage.code,
        'description': coverage.description,
        'base_price': coverage.base_price,
        'insurance_type': {
            'id': coverage.insurance_type.id,
            'name': coverage.insurance_type.name,
        }
    } for coverage in coverages]
    return Response(data)
