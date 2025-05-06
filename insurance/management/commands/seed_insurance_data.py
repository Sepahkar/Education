from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from insurance.models import Customer, InsuranceCompany, InsuranceType, Coverage, Policy, Annex
import random

class Command(BaseCommand):
    help = 'Seed the database with initial insurance test data'

    def handle(self, *args, **options):
        self.stdout.write('Seeding insurance data...')
        
        # Create insurance companies
        self.create_insurance_companies()
        
        # Create insurance types
        insurance_types = self.create_insurance_types()
        
        # Create coverages for each insurance type
        self.create_coverages(insurance_types)
        
        # Create test customers
        customers = self.create_customers()
        
        # Create policies
        policies = self.create_policies(customers)
        
        # Create annexes
        self.create_annexes(policies)
        
        self.stdout.write(self.style.SUCCESS('Successfully seeded insurance data'))

    def create_insurance_companies(self):
        companies = [
            {
                'name': 'بیمه ایران',
                'code': 'IRAN',
                'logo_url': 'https://iraninsurance.ir/images/logo.png',
                'website': 'https://iraninsurance.ir',
                'description': 'بزرگترین شرکت بیمه دولتی ایران',
            },
            {
                'name': 'بیمه آسیا',
                'code': 'ASIA',
                'logo_url': 'https://www.bimehasia.com/images/logo.png',
                'website': 'https://www.bimehasia.com',
                'description': 'شرکت بیمه آسیا',
            },
            {
                'name': 'بیمه البرز',
                'code': 'ALBORZ',
                'logo_url': 'https://www.alborzinsurance.ir/images/logo.png',
                'website': 'https://www.alborzinsurance.ir',
                'description': 'شرکت بیمه البرز',
            },
            {
                'name': 'بیمه دانا',
                'code': 'DANA',
                'logo_url': 'https://www.dana-insurance.com/images/logo.png',
                'website': 'https://www.dana-insurance.com',
                'description': 'شرکت بیمه دانا',
            },
            {
                'name': 'بیمه پارسیان',
                'code': 'PARSIAN',
                'logo_url': 'https://www.parsianinsurance.ir/images/logo.png',
                'website': 'https://www.parsianinsurance.ir',
                'description': 'شرکت بیمه پارسیان',
            },
            {
                'name': 'بیمه سامان',
                'code': 'SAMAN',
                'logo_url': 'https://www.samaninsurance.ir/images/logo.png',
                'website': 'https://www.samaninsurance.ir', 
                'description': 'شرکت بیمه سامان',
            },
            {
                'name': 'بیمه ملت',
                'code': 'MELLAT',
                'logo_url': 'https://www.mellatinsurance.com/images/logo.png',
                'website': 'https://www.mellatinsurance.com',
                'description': 'شرکت بیمه ملت',
            },
        ]
        
        created_companies = []
        for company_data in companies:
            company, created = InsuranceCompany.objects.get_or_create(
                code=company_data['code'],
                defaults=company_data
            )
            created_companies.append(company)
            action = 'Created' if created else 'Updated'
            self.stdout.write(f"{action} insurance company: {company.name}")
        
        return created_companies

    def create_insurance_types(self):
        types = [
            {
                'name': 'شخص ثالث',
                'code': 'THIRD_PARTY',
                'description': 'بیمه شخص ثالث خودرو - پوشش خسارات مالی و جانی',
            },
            {
                'name': 'بدنه',
                'code': 'CAR_BODY',
                'description': 'بیمه بدنه خودرو - پوشش خسارات وارده به خودرو',
            },
            {
                'name': 'آتش‌سوزی',
                'code': 'FIRE',
                'description': 'بیمه آتش‌سوزی منازل و اماکن تجاری',
            },
            {
                'name': 'درمان تکمیلی',
                'code': 'HEALTH',
                'description': 'بیمه درمان تکمیلی - پوشش هزینه‌های درمانی',
            },
            {
                'name': 'مسئولیت',
                'code': 'LIABILITY',
                'description': 'بیمه مسئولیت حرفه‌ای و عمومی',
            },
            {
                'name': 'عمر و سرمایه‌گذاری',
                'code': 'LIFE',
                'description': 'بیمه عمر و سرمایه‌گذاری',
            },
        ]
        
        created_types = []
        for type_data in types:
            ins_type, created = InsuranceType.objects.get_or_create(
                code=type_data['code'],
                defaults=type_data
            )
            created_types.append(ins_type)
            action = 'Created' if created else 'Updated'
            self.stdout.write(f"{action} insurance type: {ins_type.name}")
        
        return created_types

    def create_coverages(self, insurance_types):
        # Get the insurance types by code for easier reference
        types_dict = {t.code: t for t in insurance_types}
        
        coverages = [
            # شخص ثالث
            {
                'name': 'پوشش خسارت مالی',
                'code': 'THIRD_FINANCIAL',
                'description': 'پوشش خسارت مالی تا سقف 400 میلیون ریال',
                'base_price': 20000000,  # 2 میلیون تومان
                'insurance_type': types_dict['THIRD_PARTY'],
            },
            {
                'name': 'پوشش خسارت جانی',
                'code': 'THIRD_BODY',
                'description': 'پوشش خسارت جانی مطابق با دیه سال',
                'base_price': 10000000,  # 1 میلیون تومان
                'insurance_type': types_dict['THIRD_PARTY'],
            },
            {
                'name': 'پوشش تکمیلی مازاد دیه',
                'code': 'THIRD_EXTRA',
                'description': 'پوشش تکمیلی مازاد دیه',
                'base_price': 5000000,  # 500 هزار تومان
                'insurance_type': types_dict['THIRD_PARTY'],
            },
            
            # بدنه
            {
                'name': 'پوشش سرقت کلی',
                'code': 'BODY_THEFT',
                'description': 'پوشش سرقت کلی خودرو',
                'base_price': 15000000,  # 1.5 میلیون تومان
                'insurance_type': types_dict['CAR_BODY'],
            },
            {
                'name': 'پوشش آتش‌سوزی',
                'code': 'BODY_FIRE',
                'description': 'پوشش آتش‌سوزی خودرو',
                'base_price': 10000000,  # 1 میلیون تومان
                'insurance_type': types_dict['CAR_BODY'],
            },
            {
                'name': 'پوشش خسارت کامل',
                'code': 'BODY_FULL',
                'description': 'پوشش کامل خسارات وارده به بدنه خودرو',
                'base_price': 30000000,  # 3 میلیون تومان
                'insurance_type': types_dict['CAR_BODY'],
            },
            
            # آتش‌سوزی
            {
                'name': 'پوشش آتش‌سوزی ساختمان',
                'code': 'FIRE_BUILDING',
                'description': 'پوشش آتش‌سوزی ساختمان',
                'base_price': 20000000,  # 2 میلیون تومان
                'insurance_type': types_dict['FIRE'],
            },
            {
                'name': 'پوشش انفجار',
                'code': 'FIRE_EXPLOSION',
                'description': 'پوشش خسارات ناشی از انفجار',
                'base_price': 15000000,  # 1.5 میلیون تومان
                'insurance_type': types_dict['FIRE'],
            },
            
            # درمان تکمیلی
            {
                'name': 'پوشش بستری',
                'code': 'HEALTH_HOSPITAL',
                'description': 'پوشش هزینه‌های بستری تا سقف 500 میلیون تومان',
                'base_price': 50000000,  # 5 میلیون تومان
                'insurance_type': types_dict['HEALTH'],
            },
            {
                'name': 'پوشش دندانپزشکی',
                'code': 'HEALTH_DENTAL',
                'description': 'پوشش هزینه‌های دندانپزشکی تا سقف 50 میلیون تومان',
                'base_price': 20000000,  # 2 میلیون تومان
                'insurance_type': types_dict['HEALTH'],
            },
            {
                'name': 'پوشش عینک و لنز',
                'code': 'HEALTH_OPTICAL',
                'description': 'پوشش هزینه‌های عینک و لنز تا سقف 20 میلیون تومان',
                'base_price': 10000000,  # 1 میلیون تومان
                'insurance_type': types_dict['HEALTH'],
            },
        ]
        
        created_coverages = []
        for coverage_data in coverages:
            coverage, created = Coverage.objects.get_or_create(
                code=coverage_data['code'],
                defaults=coverage_data
            )
            created_coverages.append(coverage)
            action = 'Created' if created else 'Updated'
            self.stdout.write(f"{action} coverage: {coverage.name}")
        
        return created_coverages

    def create_customers(self):
        # 10 مشتری تستی
        customers_data = [
            {
                'id': 'CUST001',
                'first_name': 'علی',
                'last_name': 'محمدی',
                'national_code': '1234567890',
                'email': 'ali@example.com',
                'phone_number': '09123456789',
                'address': 'تهران، خیابان ولیعصر',
            },
            {
                'id': 'CUST002',
                'first_name': 'مریم',
                'last_name': 'احمدی',
                'national_code': '2345678901',
                'email': 'maryam@example.com',
                'phone_number': '09123456780',
                'address': 'اصفهان، چهارباغ',
            },
            {
                'id': 'CUST003',
                'first_name': 'رضا',
                'last_name': 'کریمی',
                'national_code': '3456789012',
                'email': 'reza@example.com',
                'phone_number': '09123456781',
                'address': 'مشهد، بلوار وکیل‌آباد',
            },
            {
                'id': 'CUST004',
                'first_name': 'فاطمه',
                'last_name': 'حسینی',
                'national_code': '4567890123',
                'email': 'fateme@example.com',
                'phone_number': '09123456782',
                'address': 'شیراز، بلوار زند',
            },
            {
                'id': 'CUST005',
                'first_name': 'محمد',
                'last_name': 'رضایی',
                'national_code': '5678901234',
                'email': 'mohammad@example.com',
                'phone_number': '09123456783',
                'address': 'تبریز، خیابان امام',
            },
            {
                'id': 'CUST006',
                'first_name': 'زهرا',
                'last_name': 'نجفی',
                'national_code': '6789012345',
                'email': 'zahra@example.com',
                'phone_number': '09123456784',
                'address': 'قم، خیابان ارم',
            },
            {
                'id': 'CUST007',
                'first_name': 'حسین',
                'last_name': 'موسوی',
                'national_code': '7890123456',
                'email': 'hossein@example.com',
                'phone_number': '09123456785',
                'address': 'کرج، مهرشهر',
            },
            {
                'id': 'CUST008',
                'first_name': 'سارا',
                'last_name': 'جعفری',
                'national_code': '8901234567',
                'email': 'sara@example.com',
                'phone_number': '09123456786',
                'address': 'اهواز، کیانپارس',
            },
            {
                'id': 'CUST009',
                'first_name': 'امیر',
                'last_name': 'میرزایی',
                'national_code': '9012345678',
                'email': 'amir@example.com',
                'phone_number': '09123456787',
                'address': 'رشت، خیابان لاکانی',
            },
            {
                'id': 'CUST010',
                'first_name': 'نرگس',
                'last_name': 'صادقی',
                'national_code': '0123456789',
                'email': 'narges@example.com',
                'phone_number': '09123456788',
                'address': 'یزد، خیابان کاشانی',
            },
        ]
        
        created_customers = []
        for customer_data in customers_data:
            customer, created = Customer.objects.get_or_create(
                id=customer_data['id'],
                defaults=customer_data
            )
            created_customers.append(customer)
            action = 'Created' if created else 'Updated'
            self.stdout.write(f"{action} customer: {customer.full_name}")
        
        return created_customers

    def create_policies(self, customers):
        # Get some sample data for policies
        companies = list(InsuranceCompany.objects.all())
        types = list(InsuranceType.objects.all())
        
        # دریافت پوشش‌ها برای هر نوع بیمه
        coverages_by_type = {}
        for ins_type in types:
            coverages_by_type[ins_type.id] = list(Coverage.objects.filter(insurance_type=ins_type))
        
        # Generate 20 policies
        policies = []
        now = timezone.now().date()
        
        # Policy numbers for consistent reference
        policy_numbers = [
            'POL001', 'POL002', 'POL003', 'POL004', 'POL005',
            'POL006', 'POL007', 'POL008', 'POL009', 'POL010',
            'POL011', 'POL012', 'POL013', 'POL014', 'POL015',
            'POL016', 'POL017', 'POL018', 'POL019', 'POL020',
        ]
        
        for i in range(20):
            # Select random customer, company and type
            customer = random.choice(customers)
            company = random.choice(companies)
            ins_type = random.choice(types)
            
            # Generate issue and expiry dates
            days_ago = random.randint(0, 300)
            issue_date = now - timedelta(days=days_ago)
            expiry_date = issue_date + timedelta(days=365)  # بیمه‌نامه یکساله
            
            # Determine status based on expiry date
            status = 'active' if expiry_date > now else 'expired'
            
            # Random premium amount (between 3 to 8 million tomans)
            premium = random.randint(30000000, 80000000)
            
            # Create or update policy
            policy, created = Policy.objects.get_or_create(
                policy_number=policy_numbers[i],
                defaults={
                    'customer': customer,
                    'insurance_company': company,
                    'insurance_type': ins_type,
                    'issue_date': issue_date,
                    'expiry_date': expiry_date,
                    'premium_amount': premium,
                    'status': status,
                    'description': f'بیمه‌نامه {ins_type.name} برای {customer.full_name}',
                }
            )
            
            # Add coverages - ابتدا پاکسازی پوشش‌های قبلی
            if created:
                policy.coverages.clear()
                # اضافه کردن تمام پوشش‌های مربوط به این نوع بیمه
                for coverage in coverages_by_type[ins_type.id]:
                    policy.coverages.add(coverage)
            
            policies.append(policy)
            action = 'Created' if created else 'Updated'
            self.stdout.write(f"{action} policy: {policy.policy_number} for {customer.full_name}")
        
        # برخی بیمه‌نامه‌ها را در آستانه انقضا قرار دهیم
        for i in range(3):
            policy = policies[i]
            policy.expiry_date = now + timedelta(days=random.randint(10, 30))
            policy.status = 'active'
            policy.save()
            self.stdout.write(f"Set policy {policy.policy_number} to expire soon")
        
        return policies

    def create_annexes(self, policies):
        # Annex numbers for consistent reference
        annex_numbers = [
            'ANN001', 'ANN002', 'ANN003', 'ANN004', 'ANN005'
        ]
        
        # Create 5 annexes for different policies
        for i in range(5):
            policy = policies[i]
            ins_type = policy.insurance_type
            
            # Get available coverages for this insurance type
            all_coverages = list(Coverage.objects.filter(insurance_type=ins_type))
            current_coverages = list(policy.coverages.all())
            
            # Find coverages not in policy
            available_to_add = [c for c in all_coverages if c not in current_coverages]
            
            # Create annex date - ایجاد تاریخ الحاقیه (بین تاریخ صدور و انقضا)
            days_after_issue = random.randint(30, 90)
            issue_date = policy.issue_date + timedelta(days=days_after_issue)
            
            # انتخاب پوشش‌های اضافی یا حذفی
            coverages_to_add = []
            coverages_to_remove = []
            
            # حالت‌های مختلف: فقط اضافه، فقط حذف، یا هر دو
            action_type = random.choice(['add', 'remove', 'both'])
            
            if action_type in ['add', 'both'] and available_to_add:
                coverages_to_add = random.sample(available_to_add, min(len(available_to_add), 2))
            
            if action_type in ['remove', 'both'] and current_coverages:
                coverages_to_remove = random.sample(current_coverages, min(len(current_coverages), 1))
            
            # مبلغ اضافی
            additional_premium = random.randint(5000000, 10000000) if coverages_to_add else 0
            
            # توضیحات
            description = 'الحاقیه تغییر پوشش‌های بیمه‌نامه'
            
            # Create or update annex
            annex, created = Annex.objects.get_or_create(
                annex_number=annex_numbers[i],
                defaults={
                    'policy': policy,
                    'issue_date': issue_date,
                    'additional_premium': additional_premium,
                    'description': description,
                }
            )
            
            # Clear and add coverages if needed
            if created:
                annex.coverages_added.clear()
                annex.coverages_removed.clear()
                
                for coverage in coverages_to_add:
                    annex.coverages_added.add(coverage)
                    policy.coverages.add(coverage)
                
                for coverage in coverages_to_remove:
                    annex.coverages_removed.add(coverage)
                    policy.coverages.remove(coverage)
            
            action = 'Created' if created else 'Updated'
            self.stdout.write(f"{action} annex: {annex.annex_number} for policy {policy.policy_number}") 