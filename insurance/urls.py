from django.urls import path
from . import views

app_name = 'insurance'

urlpatterns = [
    # Basic views
    path('', views.home, name='home'),
    path('companies/', views.company_list, name='company_list'),
    path('types/', views.insurance_type_list, name='insurance_type_list'),
    
    # Customer views
    path('customer/login/', views.customer_login, name='customer_login'),
    path('customer/logout/', views.customer_logout, name='customer_logout'),
    path('customer/dashboard/', views.customer_dashboard, name='customer_dashboard'),
    path('customer/policies/', views.customer_policies, name='customer_policies'),
    path('customer/profile/', views.customer_profile, name='customer_profile'),
    
    # Policy views
    path('policy/<str:policy_number>/', views.policy_detail, name='policy_detail'),
    path('policy/<str:policy_number>/extend/', views.policy_extend, name='policy_extend'),
    path('policy/<str:policy_number>/add-annex/', views.add_annex, name='add_annex'),
    
    # API endpoints (can be expanded later)
    path('api/companies/', views.api_company_list, name='api_company_list'),
    path('api/types/', views.api_insurance_type_list, name='api_insurance_type_list'),
    path('api/coverages/', views.api_coverage_list, name='api_coverage_list'),
] 