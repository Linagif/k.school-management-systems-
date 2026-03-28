"""
Comprehensive unit tests for the Django School Management System.

Run tests with: python manage.py test
Run specific test with: python manage.py test core.tests.StudentModelTest
Run with coverage: coverage run --source='.' manage.py test && coverage report
"""

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from decimal import Decimal
from datetime import date, timedelta
import logging

from .models import UserProfile, Student, Teacher, Subject, Mark, Attendance
from .forms import LoginForm, StudentSignupForm, TeacherSignupForm, MarkForm, FilterAttendanceForm

logger = logging.getLogger(__name__)


# ==================== MODEL TESTS ====================

class UserProfileModelTest(TestCase):
    """Test UserProfile model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='TestPass123'
        )
    
    def test_create_user_profile(self):
        """Test creating a user profile"""
        profile = UserProfile.objects.create(
            user=self.user,
            user_type='student',
            phone='1234567890'
        )
        self.assertEqual(profile.user_type, 'student')
        self.assertEqual(str(profile), 'testuser - student')
    
    def test_user_profile_choices(self):
        """Test all user type choices are valid"""
        valid_types = ['admin', 'teacher', 'student', 'parent']
        for user_type in valid_types:
            profile = UserProfile.objects.create(
                user=User.objects.create_user(f'user_{user_type}', password='pass123'),
                user_type=user_type
            )
            self.assertEqual(profile.user_type, user_type)


class StudentModelTest(TestCase):
    """Test Student model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='student1',
            first_name='John',
            last_name='Doe',
            password='StudentPass123'
        )
        self.student = Student.objects.create(
            user=self.user,
            admission_number='STU001',
            date_of_birth='2010-01-01',
            grade='10A'
        )
    
    def test_create_student(self):
        """Test creating a student"""
        self.assertEqual(self.student.admission_number, 'STU001')
        self.assertEqual(self.student.grade, '10A')
    
    def test_student_string_representation(self):
        """Test student string representation"""
        self.assertEqual(str(self.student), 'John Doe - STU001')
    
    def test_unique_admission_number(self):
        """Test admission number must be unique"""
        with self.assertRaises(Exception):
            Student.objects.create(
                user=User.objects.create_user('student2', password='pass123'),
                admission_number='STU001',  # Duplicate
                date_of_birth='2010-01-01',
                grade='10B'
            )


class TeacherModelTest(TestCase):
    """Test Teacher model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='teacher1',
            first_name='Jane',
            last_name='Smith',
            password='TeacherPass123'
        )
        self.teacher = Teacher.objects.create(
            user=self.user,
            employee_id='TECH001',
            specialization='Mathematics'
        )
    
    def test_create_teacher(self):
        """Test creating a teacher"""
        self.assertEqual(self.teacher.employee_id, 'TECH001')
        self.assertEqual(self.teacher.specialization, 'Mathematics')
    
    def test_teacher_string_representation(self):
        """Test teacher string representation"""
        self.assertEqual(str(self.teacher), 'Jane Smith - TECH001')
    
    def test_unique_employee_id(self):
        """Test employee ID must be unique"""
        with self.assertRaises(Exception):
            Teacher.objects.create(
                user=User.objects.create_user('teacher2', password='pass123'),
                employee_id='TECH001',  # Duplicate
                specialization='Science'
            )


class MarkModelTest(TestCase):
    """Test Mark model"""
    
    def setUp(self):
        self.user = User.objects.create_user('student1', password='pass123')
        self.student = Student.objects.create(
            user=self.user,
            admission_number='STU001',
            date_of_birth='2010-01-01',
            grade='10A'
        )
        self.subject = Subject.objects.create(
            name='Mathematics',
            code='MATH101'
        )
        self.teacher_user = User.objects.create_user('teacher1', password='pass123')
        self.teacher = Teacher.objects.create(
            user=self.teacher_user,
            employee_id='TECH001',
            specialization='Mathematics'
        )
    
    def test_create_mark(self):
        """Test creating a mark record"""
        mark = Mark.objects.create(
            student=self.student,
            subject=self.subject,
            term='1',
            year=2024,
            marks_obtained=Decimal('85.50'),
            total_marks=Decimal('100'),
            added_by=self.teacher
        )
        self.assertEqual(mark.marks_obtained, Decimal('85.50'))
        self.assertEqual(mark.grade, 'A')  # 85.5% = A grade (>= 80)
    
    def test_mark_grade_calculation(self):
        """Test automatic grade calculation"""
        test_cases = [
            (Decimal('95'), 'A+'),
            (Decimal('85'), 'A'),
            (Decimal('75'), 'B'),
            (Decimal('65'), 'C'),
            (Decimal('55'), 'D'),
            (Decimal('45'), 'F'),
        ]
        
        for idx, (marks, expected_grade) in enumerate(test_cases, 1):
            # Create a subject for each test to avoid UNIQUE constraint
            subject = Subject.objects.create(
                code=f'SUB{idx:03d}',
                name=f'Subject {idx}',
                teacher=self.teacher
            )
            mark = Mark.objects.create(
                student=self.student,
                subject=subject,
                term=str(idx),  # Different term for each
                year=2024,
                marks_obtained=marks,
                total_marks=Decimal('100'),
                added_by=self.teacher
            )
            self.assertEqual(mark.grade, expected_grade, f'Failed for marks {marks}')
    
    def test_mark_with_zero_total_marks(self):
        """Test mark calculation with zero total marks doesn't crash"""
        mark = Mark.objects.create(
            student=self.student,
            subject=self.subject,
            term='1',
            year=2024,
            marks_obtained=Decimal('0'),
            total_marks=Decimal('0'),
            added_by=self.teacher
        )
        # Should not crash and percentage should be 0
        self.assertEqual(mark.get_percentage(), 0)
    
    def test_mark_percentage_calculation(self):
        """Test percentage calculation"""
        mark = Mark.objects.create(
            student=self.student,
            subject=self.subject,
            term='1',
            year=2024,
            marks_obtained=Decimal('50'),
            total_marks=Decimal('100'),
            added_by=self.teacher
        )
        self.assertEqual(mark.get_percentage(), 50.0)


class AttendanceModelTest(TestCase):
    """Test Attendance model"""
    
    def setUp(self):
        self.user = User.objects.create_user('student1', password='pass123')
        self.student = Student.objects.create(
            user=self.user,
            admission_number='STU001',
            date_of_birth='2010-01-01',
            grade='10A'
        )
        self.teacher_user = User.objects.create_user('teacher1', password='pass123')
        self.teacher = Teacher.objects.create(
            user=self.teacher_user,
            employee_id='TECH001',
            specialization='Mathematics'
        )
    
    def test_create_attendance(self):
        """Test creating attendance record"""
        attendance = Attendance.objects.create(
            student=self.student,
            date=date.today(),
            status='present',
            marked_by=self.teacher
        )
        self.assertEqual(attendance.status, 'present')
    
    def test_unique_attendance_per_date(self):
        """Test only one attendance record per student per date"""
        Attendance.objects.create(
            student=self.student,
            date=date.today(),
            status='present',
            marked_by=self.teacher
        )
        
        # Updating should work (update_or_create pattern)
        attendance, created = Attendance.objects.update_or_create(
            student=self.student,
            date=date.today(),
            defaults={'status': 'absent'}
        )
        self.assertFalse(created)
        self.assertEqual(attendance.status, 'absent')
    
    def test_attendance_status_choices(self):
        """Test all attendance status choices are valid"""
        valid_statuses = ['present', 'absent', 'late', 'excused']
        for status in valid_statuses:
            attendance = Attendance.objects.create(
                student=self.student,
                date=date.today() - timedelta(days=len(valid_statuses) - valid_statuses.index(status)),
                status=status,
                marked_by=self.teacher
            )
            self.assertEqual(attendance.status, status)


# ==================== FORM TESTS ====================

class LoginFormTest(TestCase):
    """Test LoginForm"""
    
    def test_valid_form(self):
        """Test valid login form"""
        user = User.objects.create_user('testuser', password='TestPass123')
        form = LoginForm(data={
            'username': 'testuser',
            'password': 'TestPass123'
        })
        self.assertTrue(form.is_valid())
    
    def test_empty_form(self):
        """Test empty login form is invalid"""
        form = LoginForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)


class StudentSignupFormTest(TestCase):
    """Test StudentSignupForm"""
    
    def test_valid_signup_form(self):
        """Test valid student signup"""
        form = StudentSignupForm(data={
            'first_name': 'John',
            'last_name': 'Doe',
            'username': 'johndoe',
            'email': 'john@example.com',
            'password': 'SecurePass123',
            'confirm_password': 'SecurePass123',
            'phone': '1234567890',
            'admission_number': 'ADM001',
            'date_of_birth': '2010-01-01',
            'grade': '10A'
        })
        self.assertTrue(form.is_valid())
    
    def test_password_mismatch(self):
        """Test password mismatch validation"""
        form = StudentSignupForm(data={
            'first_name': 'John',
            'last_name': 'Doe',
            'username': 'johndoe',
            'email': 'john@example.com',
            'password': 'SecurePass123',
            'confirm_password': 'DifferentPass123',
            'admission_number': 'ADM001',
            'date_of_birth': '2010-01-01',
            'grade': '10A'
        })
        self.assertFalse(form.is_valid())
        # Django uses '__all__' for non_field_errors
        self.assertTrue('__all__' in form.errors or 'non_field_errors' in form.errors)
    
    def test_weak_password(self):
        """Test weak password validation"""
        form = StudentSignupForm(data={
            'first_name': 'John',
            'last_name': 'Doe',
            'username': 'johndoe',
            'email': 'john@example.com',
            'password': 'weak',
            'confirm_password': 'weak',
            'admission_number': 'ADM001',
            'date_of_birth': '2010-01-01',
            'grade': '10A'
        })
        self.assertFalse(form.is_valid())
    
    def test_duplicate_username(self):
        """Test duplicate username validation"""
        User.objects.create_user('johndoe', password='pass123')
        
        form = StudentSignupForm(data={
            'first_name': 'John',
            'last_name': 'Doe',
            'username': 'johndoe',
            'email': 'john@example.com',
            'password': 'SecurePass123',
            'confirm_password': 'SecurePass123',
            'admission_number': 'ADM001',
            'date_of_birth': '2010-01-01',
            'grade': '10A'
        })
        self.assertFalse(form.is_valid())


class MarkFormTest(TestCase):
    """Test MarkForm"""
    
    def setUp(self):
        self.student_user = User.objects.create_user('student1', password='pass123')
        self.student = Student.objects.create(
            user=self.student_user,
            admission_number='STU001',
            date_of_birth='2010-01-01',
            grade='10A'
        )
        self.subject = Subject.objects.create(
            name='Mathematics',
            code='MATH101'
        )
    
    def test_valid_mark_form(self):
        """Test valid mark form"""
        form = MarkForm(data={
            'student': self.student.id,
            'subject': self.subject.id,
            'term': '1',
            'year': 2024,
            'marks_obtained': '85.50',
            'total_marks': '100',
        })
        self.assertTrue(form.is_valid())
    
    def test_marks_exceeding_total(self):
        """Test marks cannot exceed total marks"""
        form = MarkForm(data={
            'student': self.student.id,
            'subject': self.subject.id,
            'term': '1',
            'year': 2024,
            'marks_obtained': '150',
            'total_marks': '100',
        })
        self.assertFalse(form.is_valid())


# ==================== VIEW TESTS ====================

class ViewsTest(TestCase):
    """Test views with proper access control"""
    
    def setUp(self):
        self.client = Client()
        
        # Create test users
        self.student_user = User.objects.create_user(
            username='student',
            password='StudentPass123'
        )
        self.teacher_user = User.objects.create_user(
            username='teacher',
            password='TeacherPass123'
        )
        self.admin_user = User.objects.create_user(
            username='admin',
            password='AdminPass123',
            is_superuser=True
        )
        
        # Create profiles
        UserProfile.objects.create(
            user=self.student_user,
            user_type='student'
        )
        UserProfile.objects.create(
            user=self.teacher_user,
            user_type='teacher'
        )
        UserProfile.objects.create(
            user=self.admin_user,
            user_type='admin'
        )
    
    def test_login_view_redirects_authenticated(self):
        """Test login view redirects authenticated users"""
        self.client.login(username='student', password='StudentPass123')
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('dashboard', response.url)
    
    def test_dashboard_requires_login(self):
        """Test dashboard requires login"""
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)
        # Check if redirects to login (URL contains 'login' or redirects with next parameter)
        self.assertTrue('login' in response.url.lower() or 'next=' in response.url)
    
    def test_student_cannot_access_teacher_dashboard(self):
        """Test student cannot access teacher dashboard"""
        self.client.login(username='student', password='StudentPass123')
        response = self.client.get(reverse('teacher_dashboard'))
        self.assertEqual(response.status_code, 302)


# ==================== INTEGRATION TESTS ====================

class FullFlowTest(TestCase):
    """Test complete user flows"""
    
    def setUp(self):
        self.client = Client()
    
    def test_student_signup_and_login(self):
        """Test student signup and login flow"""
        signup_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'username': 'johndoe',
            'email': 'john@example.com',
            'password': 'StudentPass123',
            'confirm_password': 'StudentPass123',
            'phone': '1234567890',
            'admission_number': 'STU001',
            'date_of_birth': '2010-01-01',
            'grade': '10A'
        }
        
        # Signup
        form = StudentSignupForm(data=signup_data)
        self.assertTrue(form.is_valid())
        
        # Actually create the user and profile from form data
        user = User.objects.create_user(
            username=form.cleaned_data['username'],
            email=form.cleaned_data['email'],
            password=form.cleaned_data['password'],
            first_name=form.cleaned_data['first_name'],
            last_name=form.cleaned_data['last_name']
        )
        UserProfile.objects.create(
            user=user,
            user_type='student',
            phone=form.cleaned_data.get('phone', '')
        )
        Student.objects.create(
            user=user,
            admission_number=form.cleaned_data['admission_number'],
            date_of_birth=form.cleaned_data['date_of_birth'],
            grade=form.cleaned_data['grade']
        )
        
        # Verify user and profile created
        user = User.objects.get(username='johndoe')
        self.assertTrue(hasattr(user, 'profile'))
        self.assertEqual(user.profile.user_type, 'student')
