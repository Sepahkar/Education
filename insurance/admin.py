from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count, Sum, Q
from django.utils import timezone
from django import forms
from datetime import timedelta
from .models import Customer, InsuranceCompany, InsuranceType, Coverage, Policy, Annex

# تنظیم عنوان پنل ادمین
admin.site.site_header = 'پنل مدیریت سامانه فروش بیمه'
admin.site.site_title = 'مدیریت بیمه'
admin.site.index_title = 'مدیریت سامانه بیمه'


class InsuranceAdminBase(admin.ModelAdmin):
    """کلاس پایه برای تنظیمات مشترک ادمین"""
    
    # اضافه کردن دکمه‌های ذخیره در بالا و پایین فرم
    save_on_top = True
    
    def get_readonly_fields(self, request, obj=None):
        """فیلدهای created_at و updated_at فقط خواندنی هستند"""
        return list(self.readonly_fields) + ['created_at', 'updated_at']


@admin.register(Customer)
class CustomerAdmin(InsuranceAdminBase):
    list_display = ('id', 'full_name', 'national_code', 'phone_number', 'active_policies_count', 'jalali_created_date')
    search_fields = ('id', 'first_name', 'last_name', 'national_code', 'phone_number', 'email')
    list_filter = ('created_at',)
    
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('id', 'first_name', 'last_name', 'national_code')
        }),
        ('اطلاعات تماس', {
            'fields': ('phone_number', 'email', 'address')
        }),
        ('اطلاعات سیستمی', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def active_policies_count(self, obj):
        return obj.policies.filter(status='active').count()
    active_policies_count.short_description = 'بیمه‌نامه‌های فعال'
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # در حالت ویرایش
            return super().get_readonly_fields(request, obj) + ['id', 'national_code']
        return super().get_readonly_fields(request, obj)


@admin.register(InsuranceCompany)
class InsuranceCompanyAdmin(InsuranceAdminBase):
    list_display = ('name', 'code', 'display_logo', 'website_link', 'active_policies_count', 'is_active')
    search_fields = ('name', 'code', 'website')
    list_filter = ('is_active',)
    
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('name', 'code', 'logo_url', 'website')
        }),
        ('تنظیمات', {
            'fields': ('description', 'is_active')
        }),
        ('اطلاعات سیستمی', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def display_logo(self, obj):
        if obj.logo_url:
            return format_html('<img src="{}" alt="{}" height="30" />', obj.logo_url, obj.name)
        return "-"
    display_logo.short_description = 'لوگو'
    
    def website_link(self, obj):
        if obj.website:
            return format_html('<a href="{}" target="_blank">{}</a>', obj.website, obj.website)
        return "-"
    website_link.short_description = 'وب‌سایت'
    
    def active_policies_count(self, obj):
        return obj.policies.filter(status='active').count()
    active_policies_count.short_description = 'بیمه‌نامه‌های فعال'


@admin.register(InsuranceType)
class InsuranceTypeAdmin(InsuranceAdminBase):
    list_display = ('name', 'code', 'coverages_count', 'active_policies_count', 'is_active')
    search_fields = ('name', 'code', 'description')
    list_filter = ('is_active',)
    
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('name', 'code')
        }),
        ('تنظیمات', {
            'fields': ('description', 'is_active')
        }),
        ('اطلاعات سیستمی', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def coverages_count(self, obj):
        return obj.coverages.count()
    coverages_count.short_description = 'تعداد پوشش‌ها'
    
    def active_policies_count(self, obj):
        return obj.policies.filter(status='active').count()
    active_policies_count.short_description = 'بیمه‌نامه‌های فعال'


@admin.register(Coverage)
class CoverageAdmin(InsuranceAdminBase):
    list_display = ('name', 'code', 'insurance_type', 'base_price_display', 'policies_count', 'is_active')
    search_fields = ('name', 'code', 'description')
    list_filter = ('insurance_type', 'is_active')
    
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('name', 'code', 'insurance_type')
        }),
        ('تنظیمات', {
            'fields': ('description', 'base_price', 'is_active')
        }),
        ('اطلاعات سیستمی', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def base_price_display(self, obj):
        return f"{obj.base_price:,} تومان"
    base_price_display.short_description = 'قیمت پایه'
    
    def policies_count(self, obj):
        return obj.policies.count()
    policies_count.short_description = 'تعداد بیمه‌نامه‌ها'


class PolicyAdminForm(forms.ModelForm):
    """فرم سفارشی برای ادمین بیمه‌نامه"""
    class Meta:
        model = Policy
        fields = '__all__'


class AnnexInline(admin.TabularInline):
    model = Annex
    extra = 0
    readonly_fields = ('annex_number',)
    fields = ('annex_number', 'issue_date', 'description', 'additional_premium')
    classes = ['collapse']


@admin.register(Policy)
class PolicyAdmin(InsuranceAdminBase):
    form = PolicyAdminForm
    
    list_display = ('policy_number', 'customer_link', 'insurance_type', 'insurance_company', 
                   'jalali_issue_date', 'jalali_expiry_date', 'premium_amount_display', 'status_badge', 'days_to_expiry_display')
    search_fields = ('policy_number', 'customer__first_name', 'customer__last_name', 'customer__national_code', 'customer__id')
    list_filter = ('insurance_type', 'insurance_company', 'status', 'issue_date', 'expiry_date')
    filter_horizontal = ('coverages',)
    readonly_fields = ('policy_number', 'created_at', 'updated_at', 'days_to_expiry')
    inlines = [AnnexInline]
    
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('policy_number', 'customer', 'insurance_type', 'insurance_company')
        }),
        ('جزئیات بیمه‌نامه', {
            'fields': ('issue_date', 'expiry_date', 'premium_amount', 'status', 'description')
        }),
        ('پوشش‌ها', {
            'fields': ('coverages',)
        }),
        ('اطلاعات تکمیلی', {
            'fields': ('days_to_expiry', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['extend_policies', 'mark_as_expired', 'mark_as_active']
    
    def customer_link(self, obj):
        return format_html('<a href="{}">{}</a>', 
                          f'/admin/insurance/customer/{obj.customer.id}/change/', 
                          obj.customer.full_name)
    customer_link.short_description = 'مشتری'
    
    def status_badge(self, obj):
        if obj.status == 'active':
            return format_html('<span style="background-color: #28a745; color: white; padding: 3px 8px; border-radius: 5px;">فعال</span>')
        elif obj.status == 'expired':
            return format_html('<span style="background-color: #dc3545; color: white; padding: 3px 8px; border-radius: 5px;">منقضی شده</span>')
        else:
            return format_html('<span style="background-color: #6c757d; color: white; padding: 3px 8px; border-radius: 5px;">لغو شده</span>')
    status_badge.short_description = 'وضعیت'
    
    def premium_amount_display(self, obj):
        return f"{obj.premium_amount:,} تومان"
    premium_amount_display.short_description = 'حق بیمه'
    
    def days_to_expiry_display(self, obj):
        days = obj.days_to_expiry
        if days <= 0:
            return format_html('<span style="color: red;">منقضی شده</span>')
        elif days <= 30:
            return format_html('<span style="color: orange;">{} روز</span>', days)
        else:
            return f"{days} روز"
    days_to_expiry_display.short_description = 'زمان تا انقضا'
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # ویرایش
            return super().get_readonly_fields(request, obj) + ('insurance_type', 'insurance_company', 'issue_date', 'premium_amount')
        return super().get_readonly_fields(request, obj)
    
    def extend_policies(self, request, queryset):
        """تمدید بیمه‌نامه‌های انتخاب شده برای یک سال"""
        count = 0
        for policy in queryset:
            # فقط بیمه‌نامه‌های فعال یا منقضی شده تمدید می‌شوند
            if policy.status in ['active', 'expired']:
                # اگر تاریخ انقضا گذشته، از امروز یک سال تمدید می‌شود
                if policy.expiry_date < timezone.now().date():
                    policy.issue_date = timezone.now().date()
                    policy.expiry_date = timezone.now().date() + timedelta(days=365)
                else:
                    # در غیر این صورت، یک سال به تاریخ انقضای فعلی اضافه می‌شود
                    policy.expiry_date = policy.expiry_date + timedelta(days=365)
                
                policy.status = 'active'
                policy.save()
                count += 1
        
        self.message_user(request, f'{count} بیمه‌نامه با موفقیت تمدید شدند.')
    extend_policies.short_description = 'تمدید بیمه‌نامه‌های انتخاب شده برای 1 سال'
    
    def mark_as_expired(self, request, queryset):
        """تغییر وضعیت بیمه‌نامه‌های انتخاب شده به منقضی شده"""
        updated = queryset.update(status='expired')
        self.message_user(request, f'{updated} بیمه‌نامه به وضعیت منقضی شده تغییر یافتند.')
    mark_as_expired.short_description = 'تغییر وضعیت به منقضی شده'
    
    def mark_as_active(self, request, queryset):
        """تغییر وضعیت بیمه‌نامه‌های انتخاب شده به فعال"""
        updated = queryset.update(status='active')
        self.message_user(request, f'{updated} بیمه‌نامه به وضعیت فعال تغییر یافتند.')
    mark_as_active.short_description = 'تغییر وضعیت به فعال'


@admin.register(Annex)
class AnnexAdmin(InsuranceAdminBase):
    list_display = ('annex_number', 'policy_link', 'jalali_issue_date', 'additional_premium_display', 'coverages_added_count', 'coverages_removed_count')
    search_fields = ('annex_number', 'policy__policy_number', 'policy__customer__first_name', 'policy__customer__last_name')
    list_filter = ('issue_date',)
    filter_horizontal = ('coverages_added', 'coverages_removed')
    readonly_fields = ('annex_number', 'created_at', 'updated_at')
    
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('annex_number', 'policy', 'issue_date')
        }),
        ('جزئیات الحاقیه', {
            'fields': ('description', 'additional_premium')
        }),
        ('تغییرات پوشش‌ها', {
            'fields': ('coverages_added', 'coverages_removed')
        }),
        ('اطلاعات سیستمی', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def policy_link(self, obj):
        return format_html('<a href="{}">{}</a>', 
                          f'/admin/insurance/policy/{obj.policy.policy_number}/change/', 
                          obj.policy.policy_number)
    policy_link.short_description = 'بیمه‌نامه'
    
    def additional_premium_display(self, obj):
        return f"{obj.additional_premium:,} تومان"
    additional_premium_display.short_description = 'حق بیمه اضافی'
    
    def coverages_added_count(self, obj):
        return obj.coverages_added.count()
    coverages_added_count.short_description = 'پوشش‌های اضافه شده'
    
    def coverages_removed_count(self, obj):
        return obj.coverages_removed.count()
    coverages_removed_count.short_description = 'پوشش‌های حذف شده'
