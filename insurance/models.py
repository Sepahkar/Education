from django.db import models
from django.utils.translation import gettext_lazy as _
from jalali_date import datetime2jalali, date2jalali
from django.core.validators import RegexValidator
import uuid
from django.utils import timezone

def generate_customer_id():
    return f"CUST{str(uuid.uuid4())[:6].upper()}"

def generate_policy_number():
    return f"POL{str(uuid.uuid4())[:6].upper()}"

def generate_annex_number():
    return f"ANN{str(uuid.uuid4())[:6].upper()}"

class Customer(models.Model):
    """
    مدل مشتریان بیمه
    """
    id = models.CharField(primary_key=True, max_length=10, default=generate_customer_id)
    first_name = models.CharField(_("نام"), max_length=100)
    last_name = models.CharField(_("نام خانوادگی"), max_length=100)
    national_code = models.CharField(
        _("کد ملی"),
        max_length=10, 
        validators=[
            RegexValidator(
                regex=r'^\d{10}$',
                message=_("کد ملی باید 10 رقم باشد"),
                code='invalid_national_code'
            ),
        ],
        unique=True
    )
    email = models.EmailField(_("ایمیل"), blank=True, null=True)
    phone_number = models.CharField(
        _("شماره تماس"),
        max_length=11,
        validators=[
            RegexValidator(
                regex=r'^09\d{9}$',
                message=_("شماره تماس باید با 09 شروع شود و 11 رقم باشد"),
                code='invalid_phone_number'
            ),
        ],
    )
    address = models.TextField(_("آدرس"), blank=True, null=True)
    created_at = models.DateTimeField(_("تاریخ ثبت"), auto_now_add=True)
    updated_at = models.DateTimeField(_("تاریخ بروزرسانی"), auto_now=True)

    class Meta:
        verbose_name = _("مشتری")
        verbose_name_plural = _("مشتریان")
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.id})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def jalali_created_date(self):
        return datetime2jalali(self.created_at).strftime('%Y/%m/%d')


class InsuranceCompany(models.Model):
    """
    مدل شرکت های بیمه
    """
    name = models.CharField(_("نام شرکت"), max_length=100)
    code = models.CharField(_("کد شرکت"), max_length=20, unique=True)
    logo_url = models.URLField(_("آدرس لوگو"), blank=True, null=True)
    website = models.URLField(_("وب سایت رسمی"), blank=True, null=True)
    description = models.TextField(_("توضیحات"), blank=True, null=True)
    is_active = models.BooleanField(_("فعال"), default=True)
    created_at = models.DateTimeField(_("تاریخ ثبت"), auto_now_add=True)
    updated_at = models.DateTimeField(_("تاریخ بروزرسانی"), auto_now=True)

    class Meta:
        verbose_name = _("شرکت بیمه")
        verbose_name_plural = _("شرکت های بیمه")
        ordering = ['name']

    def __str__(self):
        return self.name


class InsuranceType(models.Model):
    """
    مدل انواع بیمه
    """
    name = models.CharField(_("نام نوع بیمه"), max_length=100)
    code = models.CharField(_("کد نوع بیمه"), max_length=20, unique=True)
    description = models.TextField(_("توضیحات"), blank=True, null=True)
    is_active = models.BooleanField(_("فعال"), default=True)
    created_at = models.DateTimeField(_("تاریخ ثبت"), auto_now_add=True)
    updated_at = models.DateTimeField(_("تاریخ بروزرسانی"), auto_now=True)

    class Meta:
        verbose_name = _("نوع بیمه")
        verbose_name_plural = _("انواع بیمه")
        ordering = ['name']

    def __str__(self):
        return self.name


class Coverage(models.Model):
    """
    مدل پوشش های بیمه
    """
    name = models.CharField(_("نام پوشش"), max_length=100)
    code = models.CharField(_("کد پوشش"), max_length=20, unique=True)
    description = models.TextField(_("توضیحات"), blank=True, null=True)
    base_price = models.DecimalField(_("قیمت پایه"), max_digits=12, decimal_places=0, default=0)
    insurance_type = models.ForeignKey(
        InsuranceType,
        verbose_name=_("نوع بیمه"),
        related_name="coverages",
        on_delete=models.CASCADE
    )
    is_active = models.BooleanField(_("فعال"), default=True)
    created_at = models.DateTimeField(_("تاریخ ثبت"), auto_now_add=True)
    updated_at = models.DateTimeField(_("تاریخ بروزرسانی"), auto_now=True)

    class Meta:
        verbose_name = _("پوشش بیمه")
        verbose_name_plural = _("پوشش های بیمه")
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.insurance_type.name})"


class Policy(models.Model):
    """
    مدل بیمه نامه
    """
    STATUS_CHOICES = (
        ('active', _('فعال')),
        ('expired', _('منقضی شده')),
        ('canceled', _('لغو شده')),
    )
    
    policy_number = models.CharField(
        _("شماره بیمه نامه"), 
        primary_key=True, 
        max_length=20, 
        default=generate_policy_number
    )
    customer = models.ForeignKey(
        Customer,
        verbose_name=_("مشتری"),
        related_name="policies",
        on_delete=models.CASCADE
    )
    insurance_company = models.ForeignKey(
        InsuranceCompany,
        verbose_name=_("شرکت بیمه"),
        related_name="policies",
        on_delete=models.CASCADE
    )
    insurance_type = models.ForeignKey(
        InsuranceType,
        verbose_name=_("نوع بیمه"),
        related_name="policies",
        on_delete=models.CASCADE
    )
    coverages = models.ManyToManyField(
        Coverage,
        verbose_name=_("پوشش ها"),
        related_name="policies",
    )
    issue_date = models.DateField(_("تاریخ صدور"))
    expiry_date = models.DateField(_("تاریخ انقضاء"))
    premium_amount = models.DecimalField(_("مبلغ حق بیمه"), max_digits=12, decimal_places=0)
    status = models.CharField(_("وضعیت"), max_length=20, choices=STATUS_CHOICES, default='active')
    description = models.TextField(_("توضیحات"), blank=True, null=True)
    created_at = models.DateTimeField(_("تاریخ ثبت"), auto_now_add=True)
    updated_at = models.DateTimeField(_("تاریخ بروزرسانی"), auto_now=True)

    class Meta:
        verbose_name = _("بیمه نامه")
        verbose_name_plural = _("بیمه نامه ها")
        ordering = ['-issue_date']

    def __str__(self):
        return f"{self.policy_number} - {self.customer.full_name} - {self.insurance_type.name}"

    @property
    def jalali_issue_date(self):
        return date2jalali(self.issue_date).strftime('%Y/%m/%d')

    @property
    def jalali_expiry_date(self):
        return date2jalali(self.expiry_date).strftime('%Y/%m/%d')

    @property
    def is_expired(self):
        return self.expiry_date < timezone.now().date()
    
    @property
    def days_to_expiry(self):
        if self.is_expired:
            return 0
        delta = self.expiry_date - timezone.now().date()
        return delta.days


class Annex(models.Model):
    """
    مدل الحاقیه بیمه
    """
    annex_number = models.CharField(
        _("شماره الحاقیه"), 
        primary_key=True, 
        max_length=20, 
        default=generate_annex_number
    )
    policy = models.ForeignKey(
        Policy,
        verbose_name=_("بیمه نامه"),
        related_name="annexes",
        on_delete=models.CASCADE
    )
    description = models.TextField(_("شرح تغییرات"))
    issue_date = models.DateField(_("تاریخ صدور"))
    additional_premium = models.DecimalField(_("حق بیمه اضافی"), max_digits=12, decimal_places=0, default=0)
    coverages_added = models.ManyToManyField(
        Coverage,
        verbose_name=_("پوشش های اضافه شده"),
        related_name="annexes_added",
        blank=True
    )
    coverages_removed = models.ManyToManyField(
        Coverage,
        verbose_name=_("پوشش های حذف شده"),
        related_name="annexes_removed",
        blank=True
    )
    created_at = models.DateTimeField(_("تاریخ ثبت"), auto_now_add=True)
    updated_at = models.DateTimeField(_("تاریخ بروزرسانی"), auto_now=True)

    class Meta:
        verbose_name = _("الحاقیه")
        verbose_name_plural = _("الحاقیه ها")
        ordering = ['-issue_date']

    def __str__(self):
        return f"{self.annex_number} - {self.policy.policy_number}"

    @property
    def jalali_issue_date(self):
        return date2jalali(self.issue_date).strftime('%Y/%m/%d')
