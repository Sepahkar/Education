from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    FacultyViewSet, MajorViewSet, StudentViewSet, ProfessorViewSet,
    CourseViewSet, TermViewSet, RoomViewSet, ClassViewSet,
    EnrollmentViewSet, CourseAssignmentViewSet, ContactInfoViewSet,
    api_docs,welcome
)

router = DefaultRouter()
router.register(r'faculties', FacultyViewSet)
router.register(r'majors', MajorViewSet)
router.register(r'students', StudentViewSet)
router.register(r'professors', ProfessorViewSet)
router.register(r'courses', CourseViewSet)
router.register(r'terms', TermViewSet)
router.register(r'rooms', RoomViewSet)
router.register(r'classes', ClassViewSet)
router.register(r'enrollments', EnrollmentViewSet)
router.register(r'course-assignments', CourseAssignmentViewSet)
router.register(r'contact-infos', ContactInfoViewSet)


app_name = 'EducationApp'

urlpatterns = [
    path('', welcome, name='welcome'),
    path('api/', include(router.urls)),
    path('api/docs/', api_docs, name='api_docs'),
]