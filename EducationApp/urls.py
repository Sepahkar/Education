from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import api

# Initialize the router
router = DefaultRouter()
router.register(r'faculties', api.FacultyViewSet)
router.register(r'departments', api.DepartmentViewSet)
router.register(r'professors', api.ProfessorViewSet)
router.register(r'students', api.StudentViewSet)
router.register(r'semesters', api.SemesterViewSet)
router.register(r'rooms', api.RoomViewSet)
router.register(r'courses', api.CourseViewSet)
router.register(r'class-offerings', api.ClassOfferingViewSet)
router.register(r'class-sessions', api.ClassSessionViewSet)
router.register(r'enrollments', api.EnrollmentViewSet)
router.register(r'contacts', api.ContactInfoViewSet)

urlpatterns = [
    path('', views.welcome, name='welcome'),
    # API URLs
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),
    # Custom API docs
    path('api/docs/', views.ApiDocsView.as_view(), name='api-docs'),
    # Token auth
    path('api/token-auth/', views.ObtainAuthTokenView.as_view(), name='api_token_auth'),
    
    # Student dashboard URLs
    path('student/login/', views.student_login, name='student_login'),
    path('student/logout/', views.student_logout, name='student_logout'),
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('student/profile/', views.student_profile, name='student_profile'),
    path('student/course-selection/', views.course_selection, name='course_selection'),
] 