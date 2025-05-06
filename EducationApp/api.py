from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.contenttypes.models import ContentType
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Avg, Count
from .models import (
    Faculty, Department, Professor, Student, Semester, 
    Room, Course, ClassOffering, ClassSession, Enrollment, ContactInfo
)
from .serializers import (
    FacultySerializer, DepartmentSerializer, ProfessorSerializer, StudentSerializer,
    SemesterSerializer, RoomSerializer, CourseSerializer, ClassOfferingSerializer,
    ClassSessionSerializer, EnrollmentSerializer, ContactInfoSerializer
)

class FacultyViewSet(viewsets.ModelViewSet):
    """
    API endpoint for faculties
    """
    queryset = Faculty.objects.all()
    serializer_class = FacultySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['code', 'name']
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'code', 'establishment_date']
    
    @action(detail=True, methods=['get'])
    def departments(self, request, pk=None):
        """
        Get all departments belonging to this faculty
        """
        faculty = self.get_object()
        departments = faculty.department_set.all()
        serializer = DepartmentSerializer(departments, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def professors(self, request, pk=None):
        """
        Get all professors affiliated with this faculty
        """
        faculty = self.get_object()
        professors = Professor.objects.filter(department__faculty=faculty)
        serializer = ProfessorSerializer(professors, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def students(self, request, pk=None):
        """
        Get all students enrolled in this faculty
        """
        faculty = self.get_object()
        students = Student.objects.filter(department__faculty=faculty)
        serializer = StudentSerializer(students, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def rooms(self, request, pk=None):
        """
        Get all rooms in this faculty
        """
        faculty = self.get_object()
        rooms = faculty.room_set.all()
        serializer = RoomSerializer(rooms, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """
        Get summary statistics for this faculty
        """
        faculty = self.get_object()
        department_count = faculty.department_set.count()
        professor_count = Professor.objects.filter(department__faculty=faculty).count()
        student_count = Student.objects.filter(department__faculty=faculty).count()
        course_count = Course.objects.filter(department__faculty=faculty).count()
        room_count = faculty.room_set.count()
        
        stats = {
            'department_count': department_count,
            'professor_count': professor_count,
            'student_count': student_count,
            'course_count': course_count,
            'room_count': room_count
        }
        
        return Response(stats)

class DepartmentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for departments
    """
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['code', 'name', 'faculty']
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'code', 'establishment_date', 'faculty__name']
    
    @action(detail=True, methods=['get'])
    def courses(self, request, pk=None):
        """
        Get all courses offered by this department
        """
        department = self.get_object()
        courses = department.course_set.all()
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def professors(self, request, pk=None):
        """
        Get all professors in this department
        """
        department = self.get_object()
        professors = department.professor_set.all()
        serializer = ProfessorSerializer(professors, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def students(self, request, pk=None):
        """
        Get all students enrolled in this department
        """
        department = self.get_object()
        students = department.student_set.all()
        serializer = StudentSerializer(students, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """
        Get summary statistics for this department
        """
        department = self.get_object()
        student_count = department.student_set.count()
        professor_count = department.professor_set.count()
        course_count = department.course_set.count()
        
        stats = {
            'student_count': student_count,
            'professor_count': professor_count,
            'course_count': course_count,
            'total_credits': department.total_credits
        }
        
        return Response(stats)

class ProfessorViewSet(viewsets.ModelViewSet):
    """
    API endpoint for professors
    """
    queryset = Professor.objects.all()
    serializer_class = ProfessorSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['professor_code', 'department', 'contract_type', 'gender', 'marital_status']
    search_fields = ['first_name', 'last_name', 'national_code', 'professor_code', 'specialization']
    ordering_fields = ['last_name', 'first_name', 'employment_date', 'department__name']
    
    @action(detail=True, methods=['get'])
    def classes(self, request, pk=None):
        """
        Get all classes taught by this professor
        """
        professor = self.get_object()
        class_offerings = professor.classoffering_set.all()
        serializer = ClassOfferingSerializer(class_offerings, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def contacts(self, request, pk=None):
        """
        Get all contact information for this professor
        """
        professor = self.get_object()
        content_type = ContentType.objects.get_for_model(Professor)
        contacts = ContactInfo.objects.filter(content_type=content_type, object_id=professor.id)
        serializer = ContactInfoSerializer(contacts, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """
        Get teaching statistics for this professor
        """
        professor = self.get_object()
        total_classes = professor.classoffering_set.count()
        
        # Group classes by semester
        classes_by_semester = professor.classoffering_set.values('semester__academic_year', 'semester__semester_type') \
                            .annotate(count=Count('id')).order_by('-semester__academic_year', '-semester__semester_type')
        
        # Calculate average grades given
        avg_grade = Enrollment.objects.filter(
            class_offering__professor=professor,
            grade__isnull=False
        ).aggregate(avg_grade=Avg('grade'))
        
        # Calculate pass rate
        total_graded = Enrollment.objects.filter(
            class_offering__professor=professor,
            grade__isnull=False
        ).count()
        
        passed = Enrollment.objects.filter(
            class_offering__professor=professor,
            grade__isnull=False,
            grade__gte=10
        ).count()
        
        pass_rate = (passed / total_graded * 100) if total_graded > 0 else 0
        
        stats = {
            'total_classes': total_classes,
            'classes_by_semester': list(classes_by_semester),
            'avg_grade': avg_grade['avg_grade'] if avg_grade['avg_grade'] else 0,
            'pass_rate': round(pass_rate, 2),
            'teaching_years': professor.teaching_years
        }
        
        return Response(stats)

class StudentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for students
    """
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['student_code', 'department', 'gender', 'marital_status', 'student_status', 'military_status']
    search_fields = ['first_name', 'last_name', 'national_code', 'student_code']
    ordering_fields = ['last_name', 'first_name', 'admission_date', 'department__name']
    
    @action(detail=True, methods=['get'])
    def enrollments(self, request, pk=None):
        """
        Get all enrollments for this student
        """
        student = self.get_object()
        enrollments = student.enrollment_set.all()
        serializer = EnrollmentSerializer(enrollments, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def current_classes(self, request, pk=None):
        """
        Get current semester enrollments for this student
        """
        student = self.get_object()
        current_semester = Semester.objects.filter(is_active=True).first()
        
        if not current_semester:
            return Response({'error': 'No active semester found'}, status=404)
            
        enrollments = student.enrollment_set.filter(
            class_offering__semester=current_semester,
            status__in=['A', 'P']
        )
        
        serializer = EnrollmentSerializer(enrollments, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def contacts(self, request, pk=None):
        """
        Get all contact information for this student
        """
        student = self.get_object()
        content_type = ContentType.objects.get_for_model(Student)
        contacts = ContactInfo.objects.filter(content_type=content_type, object_id=student.id)
        serializer = ContactInfoSerializer(contacts, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def transcript(self, request, pk=None):
        """
        Get academic transcript for this student
        """
        student = self.get_object()
        
        # Get completed enrollments with grades
        enrollments = student.enrollment_set.filter(
            grade__isnull=False
        ).order_by('class_offering__semester__academic_year', 'class_offering__semester__semester_type')
        
        serializer = EnrollmentSerializer(enrollments, many=True)
        
        # Calculate GPA and other statistics
        passed_courses = student.enrollment_set.filter(grade__gte=10).count()
        failed_courses = student.enrollment_set.filter(grade__lt=10, grade__isnull=False).count()
        current_courses = student.enrollment_set.filter(status__in=['A', 'P'], grade__isnull=True).count()
        
        # Use the serializer method to get GPA and credits
        student_serializer = StudentSerializer(student)
        gpa = student_serializer.get_gpa(student)
        total_credits_earned = student_serializer.get_total_credits_earned(student)
        remaining_credits = student_serializer.get_remaining_credits(student)
        
        transcript = {
            'student': {
                'id': student.id,
                'name': student.full_name,
                'student_code': student.student_code,
                'department': student.department.name,
                'admission_date': student.jalali_admission_date,
                'status': student.get_student_status_display()
            },
            'academic_summary': {
                'gpa': gpa,
                'total_credits_earned': total_credits_earned,
                'remaining_credits': remaining_credits,
                'passed_courses': passed_courses,
                'failed_courses': failed_courses,
                'current_courses': current_courses
            },
            'enrollments': serializer.data
        }
        
        return Response(transcript)

class SemesterViewSet(viewsets.ModelViewSet):
    """
    API endpoint for semesters
    """
    queryset = Semester.objects.all()
    serializer_class = SemesterSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['academic_year', 'semester_type', 'is_active']
    search_fields = ['academic_year']
    ordering_fields = ['academic_year', 'semester_type', 'start_date']
    
    @action(detail=True, methods=['get'])
    def classes(self, request, pk=None):
        """
        Get all classes offered in this semester
        """
        semester = self.get_object()
        classes = semester.classoffering_set.all()
        serializer = ClassOfferingSerializer(classes, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """
        Get statistics for this semester
        """
        semester = self.get_object()
        
        # Count classes, enrollments
        class_count = semester.classoffering_set.count()
        enrollment_count = Enrollment.objects.filter(class_offering__semester=semester).count()
        
        # Count active students this semester
        active_students = Student.objects.filter(
            enrollment__class_offering__semester=semester,
            enrollment__status__in=['A', 'P']
        ).distinct().count()
        
        # Count professors teaching this semester
        active_professors = Professor.objects.filter(
            classoffering__semester=semester
        ).distinct().count()
        
        stats = {
            'class_count': class_count,
            'enrollment_count': enrollment_count,
            'active_students': active_students,
            'active_professors': active_professors,
            'is_current': semester.is_current,
            'start_date': semester.jalali_start_date,
            'end_date': semester.jalali_end_date
        }
        
        return Response(stats)

class RoomViewSet(viewsets.ModelViewSet):
    """
    API endpoint for rooms
    """
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['room_number', 'faculty', 'floor', 'has_projector']
    search_fields = ['room_number', 'description']
    ordering_fields = ['room_number', 'capacity', 'faculty__name', 'floor']
    
    @action(detail=True, methods=['get'])
    def sessions(self, request, pk=None):
        """
        Get all class sessions scheduled in this room
        """
        room = self.get_object()
        sessions = room.classsession_set.all()
        serializer = ClassSessionSerializer(sessions, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def schedule(self, request, pk=None):
        """
        Get the weekly schedule for this room
        """
        room = self.get_object()
        
        # Optional semester filter
        semester_id = request.query_params.get('semester')
        if semester_id:
            sessions = room.classsession_set.filter(class_offering__semester_id=semester_id)
        else:
            # Default to active semester
            active_semester = Semester.objects.filter(is_active=True).first()
            if active_semester:
                sessions = room.classsession_set.filter(class_offering__semester=active_semester)
            else:
                sessions = room.classsession_set.all()
        
        # Organize sessions by weekday
        weekly_schedule = {}
        for day_num, day_name in dict(WEEKDAY_CHOICES).items():
            day_sessions = sessions.filter(weekday=day_num).order_by('start_time')
            weekly_schedule[day_name] = ClassSessionSerializer(day_sessions, many=True).data
        
        return Response(weekly_schedule)

class CourseViewSet(viewsets.ModelViewSet):
    """
    API endpoint for courses
    """
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['course_code', 'department', 'credits', 'is_practical']
    search_fields = ['title', 'course_code', 'description']
    ordering_fields = ['title', 'course_code', 'department__name', 'credits']
    
    @action(detail=True, methods=['get'])
    def classes(self, request, pk=None):
        """
        Get all class offerings for this course
        """
        course = self.get_object()
        
        # Optional semester filter
        semester_id = request.query_params.get('semester')
        if semester_id:
            classes = course.classoffering_set.filter(semester_id=semester_id)
        else:
            classes = course.classoffering_set.all()
            
        serializer = ClassOfferingSerializer(classes, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def prerequisites(self, request, pk=None):
        """
        Get all prerequisites for this course
        """
        course = self.get_object()
        prerequisites = course.prerequisites.all()
        serializer = CourseSerializer(prerequisites, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def dependent_courses(self, request, pk=None):
        """
        Get all courses that have this course as a prerequisite
        """
        course = self.get_object()
        dependent_courses = Course.objects.filter(prerequisites=course)
        serializer = CourseSerializer(dependent_courses, many=True)
        return Response(serializer.data)

class ClassOfferingViewSet(viewsets.ModelViewSet):
    """
    API endpoint for class offerings
    """
    queryset = ClassOffering.objects.all()
    serializer_class = ClassOfferingSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['course', 'semester', 'professor', 'class_code']
    search_fields = ['class_code', 'course__title', 'professor__last_name']
    ordering_fields = ['course__title', 'semester__academic_year', 'professor__last_name']
    
    @action(detail=True, methods=['get'])
    def sessions(self, request, pk=None):
        """
        Get all sessions for this class offering
        """
        class_offering = self.get_object()
        sessions = class_offering.classsession_set.all()
        serializer = ClassSessionSerializer(sessions, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def enrollments(self, request, pk=None):
        """
        Get all enrollments for this class offering
        """
        class_offering = self.get_object()
        enrollments = class_offering.enrollment_set.all()
        serializer = EnrollmentSerializer(enrollments, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def students(self, request, pk=None):
        """
        Get all students enrolled in this class
        """
        class_offering = self.get_object()
        students = Student.objects.filter(
            enrollment__class_offering=class_offering,
            enrollment__status__in=['A', 'P']
        )
        serializer = StudentSerializer(students, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """
        Get statistics for this class offering
        """
        class_offering = self.get_object()
        
        # Enrollment statistics
        total_enrollments = class_offering.enrollment_set.count()
        approved_enrollments = class_offering.enrollment_set.filter(status='A').count()
        pending_enrollments = class_offering.enrollment_set.filter(status='P').count()
        rejected_enrollments = class_offering.enrollment_set.filter(status='R').count()
        
        # Grade statistics if available
        graded_enrollments = class_offering.enrollment_set.filter(grade__isnull=False)
        avg_grade = graded_enrollments.aggregate(avg=Avg('grade'))['avg'] if graded_enrollments.exists() else None
        
        # Pass rate
        if graded_enrollments.exists():
            passed_count = graded_enrollments.filter(grade__gte=10).count()
            pass_rate = (passed_count / graded_enrollments.count()) * 100
        else:
            pass_rate = None
        
        stats = {
            'capacity': class_offering.capacity,
            'enrolled_count': class_offering.enrolled_count,
            'remaining_capacity': class_offering.remaining_capacity,
            'enrollment_stats': {
                'total': total_enrollments,
                'approved': approved_enrollments,
                'pending': pending_enrollments,
                'rejected': rejected_enrollments
            },
            'grade_stats': {
                'average_grade': avg_grade,
                'pass_rate': pass_rate
            }
        }
        
        return Response(stats)

class ClassSessionViewSet(viewsets.ModelViewSet):
    """
    API endpoint for class sessions
    """
    queryset = ClassSession.objects.all()
    serializer_class = ClassSessionSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['class_offering', 'room', 'weekday']
    search_fields = ['class_offering__course__title', 'room__room_number']
    ordering_fields = ['weekday', 'start_time', 'class_offering__course__title']

class EnrollmentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for enrollments
    """
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['student', 'class_offering', 'status']
    search_fields = ['student__last_name', 'class_offering__course__title']
    ordering_fields = ['enrollment_date', 'grade']

class ContactInfoViewSet(viewsets.ModelViewSet):
    """
    API endpoint for contact information
    """
    queryset = ContactInfo.objects.all()
    serializer_class = ContactInfoSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['content_type', 'object_id', 'contact_type', 'is_primary']
    search_fields = ['value']
    ordering_fields = ['contact_type', 'is_primary'] 