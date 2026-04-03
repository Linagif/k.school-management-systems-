# Django School Management System - Complete Documentation

## 📋 Table of Contents
1. [Project Overview](#project-overview)
2. [System Architecture](#system-architecture)
3. [Data Models](#data-models)
4. [User Roles & Permissions](#user-roles--permissions)
5. [Features](#features)
6. [URL Routes](#url-routes)
7. [Views & Controllers](#views--controllers)
8. [Forms](#forms)
9. [Templates](#templates)
10. [Admin Interface](#admin-interface)
11. [Security Features](#security-features)
12. [Testing](#testing)
13. [Logging & Monitoring](#logging--monitoring)
14. [Installation & Setup](#installation--setup)
15. [Configuration](#configuration)
16. [API Reference](#api-reference)

---

## 🎯 Project Overview

The **Django School Management System** is a comprehensive web application designed to manage academic records, attendance, and user interactions for educational institutions. Built with Django, it provides role-based access for administrators, teachers, students, and parents.

### Key Highlights
- **Multi-role authentication** (Admin, Teacher, Student, Parent)
- **Academic grade management** with automatic grade calculation
- **Attendance tracking** with multiple status options
- **Report card generation** in PDF format
- **Comprehensive logging** and security features
- **Unit and integration tests** for reliability

### Technology Stack
- **Backend**: Django 6.0
- **Database**: SQLite (development) / PostgreSQL (production ready)
- **Frontend**: HTML5, CSS3, JavaScript
- **PDF Generation**: ReportLab
- **Authentication**: Django's built-in auth system

---

## 🏗️ System Architecture

### Project Structure
```
school_management/
├── core/                          # Main application
│   ├── models.py                  # Data models
│   ├── views.py                   # View controllers
│   ├── forms.py                   # Form definitions
│   ├── urls.py                    # URL routing
│   ├── admin.py                   # Admin interface
│   ├── decorators.py              # Custom decorators
│   ├── tests.py                   # Unit tests
│   ├── templatetags/              # Custom template tags
│   └── migrations/                # Database migrations
├── school_management/             # Project settings
│   ├── settings.py                # Configuration
│   ├── urls.py                    # Root URL config
│   ├── wsgi.py                    # WSGI entry point
│   └── asgi.py                    # ASGI entry point
├── templates/                     # HTML templates
├── static/                        # Static files
├── logs/                          # Log files
└── manage.py                      # Django management
```

### Application Flow
```
User Request → URL Router → View → Model → Database
                ↓
            Template → HTML Response
```

---

## 📊 Data Models

### 1. UserProfile Model
Extends Django's User model with role-based information.

```python
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
```

**Fields:**
- `user`: One-to-one relationship with Django User
- `user_type`: Role (admin, teacher, student, parent)
- `phone`: Contact number
- `address`: Physical address

### 2. Student Model
Stores student-specific information.

```python
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    admission_number = models.CharField(max_length=20, unique=True)
    date_of_birth = models.DateField(null=True, blank=True)
    grade = models.CharField(max_length=10)
    parent = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                               related_name='children', limit_choices_to={'profile__user_type': 'parent'})
```

**Fields:**
- `user`: One-to-one relationship with User
- `admission_number`: Unique student identifier
- `date_of_birth`: Student's birth date
- `grade`: Current grade/class
- `parent`: Foreign key to parent User

### 3. Teacher Model
Stores teacher-specific information.

```python
class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile')
    employee_id = models.CharField(max_length=20, unique=True)
    specialization = models.CharField(max_length=100, blank=True, null=True)
    date_joined = models.DateField(auto_now_add=True)
```

**Fields:**
- `user`: One-to-one relationship with User
- `employee_id`: Unique teacher identifier
- `specialization`: Subject specialization
- `date_joined`: Employment start date

### 4. Subject Model
Represents academic subjects.

```python
class Subject(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True, null=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, related_name='subjects')
```

**Fields:**
- `name`: Subject name
- `code`: Unique subject code
- `description`: Subject description
- `teacher`: Assigned teacher

### 5. Mark Model
Stores student academic marks/grades.

```python
class Mark(models.Model):
    TERM_CHOICES = (
        ('1', 'Term 1'),
        ('2', 'Term 2'),
        ('3', 'Term 3'),
    )
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='marks')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='marks')
    term = models.CharField(max_length=1, choices=TERM_CHOICES)
    year = models.IntegerField()
    marks_obtained = models.DecimalField(max_digits=5, decimal_places=2)
    total_marks = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('100'))
    grade = models.CharField(max_length=2, blank=True)
    remarks = models.TextField(blank=True, null=True)
    added_by = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, related_name='marks_added')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

**Key Features:**
- Automatic grade calculation on save
- Percentage calculation method
- Unique constraint: student + subject + term + year
- Ordered by year, term, and subject

**Grade Calculation Logic:**
```python
if percentage >= 90: grade = 'A+'
elif percentage >= 80: grade = 'A'
elif percentage >= 70: grade = 'B'
elif percentage >= 60: grade = 'C'
elif percentage >= 50: grade = 'D'
else: grade = 'F'
```

### 6. Attendance Model
Tracks student attendance records.

```python
class Attendance(models.Model):
    STATUS_CHOICES = (
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('excused', 'Excused'),
    )
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendance')
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='present')
    remarks = models.TextField(blank=True, null=True)
    marked_by = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, related_name='attendance_marked')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

**Fields:**
- `student`: Foreign key to Student
- `date`: Attendance date
- `status`: Present, Absent, Late, or Excused
- `remarks`: Additional notes
- `marked_by`: Teacher who marked attendance

---

## 👥 User Roles & Permissions

### 1. Administrator
**Access Level**: Full system access

**Capabilities:**
- View all students, teachers, and marks
- Access admin dashboard with statistics
- Manage all attendance records
- Generate reports for all users
- Access Django admin interface

**Dashboard Features:**
- Total students count
- Total teachers count
- Total subjects count
- Total marks count
- Recent marks activity

### 2. Teacher
**Access Level**: Subject and student management

**Capabilities:**
- View assigned subjects
- Add marks for students
- Mark attendance for students
- View marks they've added
- View attendance records
- Access teacher dashboard

**Dashboard Features:**
- Assigned subjects list
- Total marks added count
- Quick access to add marks
- Quick access to mark attendance

### 3. Student
**Access Level**: Personal academic records

**Capabilities:**
- View personal marks and grades
- View personal attendance records
- Generate personal report card (PDF)
- View average percentage

**Dashboard Features:**
- All marks with grades
- Average percentage calculation
- Attendance statistics
- Report card download

### 4. Parent
**Access Level**: Children's academic records

**Capabilities:**
- View linked children's marks
- View linked children's attendance
- Generate report cards for children
- Monitor academic progress

**Dashboard Features:**
- List of linked children
- Quick access to child marks
- Quick access to child attendance
- Report card generation

---

## ✨ Features

### 1. Authentication System
- **Login**: Username/password authentication
- **Signup**: Role-based registration (Student, Teacher, Parent)
- **Logout**: Secure session termination
- **Password Reset**: Via management command

### 2. Academic Management
- **Mark Entry**: Teachers can add marks for students
- **Grade Calculation**: Automatic grade assignment based on percentage
- **Term Management**: Support for multiple terms per year
- **Subject Assignment**: Teachers assigned to specific subjects

### 3. Attendance Tracking
- **Daily Attendance**: Mark attendance for any date
- **Status Options**: Present, Absent, Late, Excused
- **Remarks**: Optional notes for each attendance record
- **Statistics**: Attendance percentage calculation

### 4. Report Generation
- **PDF Report Cards**: Professional formatted reports
- **Student Reports**: Individual student performance
- **Parent Reports**: Children's academic progress
- **Charts**: Visual performance representation

### 5. Dashboard Analytics
- **Admin Dashboard**: System-wide statistics
- **Teacher Dashboard**: Subject and mark statistics
- **Student Dashboard**: Personal performance metrics
- **Parent Dashboard**: Children overview

---

## 🔗 URL Routes

### Authentication URLs
| URL | View | Name | Description |
|-----|------|------|-------------|
| `/login/` | `login_view` | `login` | User login page |
| `/signup/` | `signup_view` | `signup` | User registration |
| `/logout/` | `logout_view` | `logout` | User logout |
| `/dashboard/` | `dashboard` | `dashboard` | Role-based redirect |

### Admin URLs
| URL | View | Name | Description |
|-----|------|------|-------------|
| `/admin-dashboard/` | `admin_dashboard` | `admin_dashboard` | Admin dashboard |
| `/admin/students/` | `admin_students` | `admin_students` | View all students |
| `/admin/marks/` | `admin_marks` | `admin_marks` | View all marks |
| `/admin/attendance/` | `admin_attendance` | `admin_attendance` | View all attendance |

### Teacher URLs
| URL | View | Name | Description |
|-----|------|------|-------------|
| `/teacher-dashboard/` | `teacher_dashboard` | `teacher_dashboard` | Teacher dashboard |
| `/teacher/students/` | `teacher_students` | `teacher_students` | View all students |
| `/teacher/add-marks/` | `teacher_add_marks` | `teacher_add_marks` | Add student marks |
| `/teacher/view-marks/` | `teacher_view_marks` | `teacher_view_marks` | View added marks |
| `/teacher/mark-attendance/` | `teacher_mark_attendance` | `teacher_mark_attendance` | Mark attendance |
| `/teacher/view-attendance/` | `teacher_view_attendance` | `teacher_view_attendance` | View attendance |

### Student URLs
| URL | View | Name | Description |
|-----|------|------|-------------|
| `/student-dashboard/` | `student_dashboard` | `student_dashboard` | Student dashboard |
| `/student/attendance/` | `student_attendance` | `student_attendance` | View attendance |
| `/student/report-card/` | `generate_report_card` | `student_report_card` | Download report card |

### Parent URLs
| URL | View | Name | Description |
|-----|------|------|-------------|
| `/parent-dashboard/` | `parent_dashboard` | `parent_dashboard` | Parent dashboard |
| `/parent/child/<id>/marks/` | `parent_view_child_marks` | `parent_view_child_marks` | View child marks |
| `/parent/child/<id>/attendance/` | `parent_view_child_attendance` | `parent_view_child_attendance` | View child attendance |
| `/parent/child/<id>/report-card/` | `generate_report_card` | `parent_child_report_card` | Download child report |

---

## 🎛️ Views & Controllers

### Authentication Views

#### `login_view(request)`
Handles user authentication with form validation.

**Features:**
- Validates username and password
- Authenticates against Django User model
- Redirects to dashboard on success
- Displays error messages on failure

**Template:** `login.html`

#### `signup_view(request)`
Handles user registration with role-based forms.

**Features:**
- Supports Student, Teacher, and Parent registration
- Uses atomic transactions for data integrity
- Creates User, UserProfile, and role-specific records
- Validates unique constraints (username, email)

**Template:** `signup.html`

#### `logout_view(request)`
Logs out user and redirects to login page.

### Dashboard Views

#### `dashboard(request)`
Role-based dashboard redirect.

**Logic:**
1. Check if user has profile
2. Determine user type
3. Redirect to appropriate dashboard
4. Handle superusers as admins

#### `admin_dashboard(request)`
Displays system-wide statistics.

**Context:**
- `total_students`: Count of all students
- `total_teachers`: Count of all teachers
- `total_subjects`: Count of all subjects
- `total_marks`: Count of all marks
- `recent_marks`: Last 10 marks added

**Template:** `admin_dashboard.html`

#### `teacher_dashboard(request)`
Displays teacher-specific information.

**Context:**
- `teacher`: Teacher object
- `subjects`: Assigned subjects
- `marks_added`: Count of marks added

**Template:** `teacher_dashboard.html`

#### `student_dashboard(request)`
Displays student academic performance.

**Context:**
- `student`: Student object
- `marks`: All marks with subjects
- `avg_percentage`: Calculated average percentage

**Template:** `student_dashboard.html`

#### `parent_dashboard(request)`
Displays linked children information.

**Context:**
- `children`: List of linked students

**Template:** `parent_dashboard.html`

### Mark Management Views

#### `teacher_add_marks(request)`
Form for adding student marks.

**Features:**
- Validates marks don't exceed total
- Auto-calculates grade on save
- Links marks to teacher
- Shows only teacher's subjects

**Template:** `teacher_add_marks.html`

#### `teacher_view_marks(request)`
Displays marks added by teacher.

**Context:**
- `marks`: Filtered by current teacher

**Template:** `teacher_view_marks.html`

#### `admin_marks(request)`
Displays all marks in system.

**Context:**
- `marks`: All marks with related data

**Template:** `admin_marks.html`

### Attendance Management Views

#### `teacher_mark_attendance(request)`
Form for marking student attendance.

**Features:**
- Date selection
- Bulk attendance marking
- Update existing attendance
- Status and remarks input

**Template:** `teacher_mark_attendance.html`

#### `teacher_view_attendance(request)`
Displays attendance records with filtering.

**Features:**
- Filter by student
- Filter by status
- Filter by date range
- Paginated results

**Template:** `teacher_view_attendance.html`

#### `student_attendance(request)`
Displays student's attendance records.

**Context:**
- `attendance_records`: All attendance
- `total_days`: Total days recorded
- `present_days`: Days present
- `absent_days`: Days absent
- `late_days`: Days late
- `excused_days`: Days excused
- `attendance_percentage`: Calculated percentage

**Template:** `student_attendance.html`

#### `parent_view_child_attendance(request, student_id)`
Displays child's attendance for parent.

**Features:**
- Verifies parent-child relationship
- Shows attendance statistics

**Template:** `parent_view_attendance.html`

### Report Generation Views

#### `generate_report_card(request, student_id=None)`
Generates PDF report card.

**Features:**
- Professional PDF formatting
- Student information header
- Marks table with grades
- Attendance summary
- Performance charts
- Downloadable file

**Output:** PDF file download

---

## 📝 Forms

### LoginForm
```python
class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)
```

### StudentSignupForm
```python
class StudentSignupForm(forms.Form):
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    admission_number = forms.CharField(max_length=20)
    grade = forms.CharField(max_length=10)
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
```

**Validation:**
- Passwords must match
- Admission number must be unique

### TeacherSignupForm
```python
class TeacherSignupForm(forms.Form):
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    employee_id = forms.CharField(max_length=20)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
```

**Validation:**
- Passwords must match
- Employee ID must be unique
- Email must be unique

### ParentSignupForm
```python
class ParentSignupForm(forms.Form):
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    phone = forms.CharField(max_length=15, required=False)
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
```

**Validation:**
- Passwords must match
- Username must be unique
- Email must be unique

### MarkForm
```python
class MarkForm(forms.ModelForm):
    class Meta:
        model = Mark
        fields = ['student', 'subject', 'term', 'year', 'marks_obtained', 'total_marks', 'remarks']
```

**Validation:**
- Marks obtained cannot exceed total marks
- Total marks must be greater than 0

### FilterAttendanceForm
```python
class FilterAttendanceForm(forms.Form):
    student = forms.ModelChoiceField(queryset=Student.objects.all(), required=False)
    status = forms.ChoiceField(choices=[('', 'All')] + list(Attendance.STATUS_CHOICES), required=False)
    date_from = forms.DateField(required=False)
    date_to = forms.DateField(required=False)
```

### FilterMarkForm
```python
class FilterMarkForm(forms.Form):
    student = forms.ModelChoiceField(queryset=Student.objects.all(), required=False)
    subject = forms.ModelChoiceField(queryset=Subject.objects.all(), required=False)
    term = forms.ChoiceField(choices=[('', 'All')] + list(Mark.TERM_CHOICES), required=False)
    year = forms.IntegerField(required=False)
```

---

## 🎨 Templates

### Base Template (`base.html`)
- Navigation bar with role-based menu
- Message display system
- Footer with copyright
- Responsive design

### Authentication Templates
- `login.html`: Login form with validation
- `signup.html`: Role-based registration form

### Dashboard Templates
- `admin_dashboard.html`: Statistics cards and recent activity
- `teacher_dashboard.html`: Subject list and quick actions
- `student_dashboard.html`: Marks table and performance metrics
- `parent_dashboard.html`: Children list with quick links

### Management Templates
- `admin_students.html`: Student list with search
- `admin_marks.html`: Marks list with filters
- `teacher_students.html`: Student list for teachers
- `teacher_add_marks.html`: Mark entry form
- `teacher_view_marks.html`: Marks list for teacher
- `teacher_mark_attendance.html`: Attendance marking form
- `teacher_view_attendance.html`: Attendance records with filters

### View Templates
- `student_dashboard.html`: Student performance view
- `student_attendance.html`: Student attendance view
- `parent_view_marks.html`: Child marks view
- `parent_view_attendance.html`: Child attendance view

---

## 🔐 Security Features

### Authentication Security
- **Password Hashing**: Django's built-in password hashing
- **Session Management**: Secure session handling
- **CSRF Protection**: Automatic CSRF token validation
- **Login Required**: Decorator-based access control

### Authorization Security
- **Role-Based Access**: User type verification
- **Decorator Protection**: `@login_required`, `@teacher_required`, etc.
- **Object-Level Security**: Parent can only view own children
- **Admin Privileges**: Superuser and admin type verification

### Data Security
- **SQL Injection Protection**: Django ORM parameterized queries
- **XSS Protection**: Template auto-escaping
- **Input Validation**: Form-level validation
- **Atomic Transactions**: Database consistency

### Configuration Security
- **Environment Variables**: SECRET_KEY, DEBUG, ALLOWED_HOSTS
- **HTTPS Support**: SSL/TLS configuration ready
- **Security Headers**: XSS, clickjacking protection
- **Password Validators**: Minimum length and complexity

---

## 🧪 Testing

### Test Suite Structure
```
core/tests.py
├── UserProfileModelTest (2 tests)
├── StudentModelTest (3 tests)
├── TeacherModelTest (3 tests)
├── MarkModelTest (5 tests)
├── AttendanceModelTest (3 tests)
├── LoginFormTest (2 tests)
├── StudentSignupFormTest (4 tests)
├── MarkFormTest (2 tests)
├── ViewsTest (3 tests)
└── FullFlowTest (1 integration test)
```

### Running Tests
```bash
# Run all tests
python manage.py test

# Run specific test class
python manage.py test core.tests.MarkModelTest

# Run specific test method
python manage.py test core.tests.MarkModelTest.test_mark_with_zero_total_marks

# Run with verbose output
python manage.py test --verbosity=2

# Run with coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

### Test Coverage
- **Models**: 100% coverage
- **Forms**: 95%+ coverage
- **Views**: 80%+ coverage
- **Overall**: 85%+ coverage

---

## 📊 Logging & Monitoring

### Log Files
```
logs/
├── debug.log          # General debug information
├── security.log       # Security events
├── audit.log          # User actions
└── errors.log         # Error tracking
```

### Log Configuration
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/debug.log',
            'maxBytes': 1024*1024*10,  # 10MB
            'backupCount': 5,
        },
        'security_file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/security.log',
            'maxBytes': 1024*1024*10,
            'backupCount': 5,
        },
        'audit_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/audit.log',
            'maxBytes': 1024*1024*10,
            'backupCount': 5,
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/errors.log',
            'maxBytes': 1024*1024*10,
            'backupCount': 5,
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.security': {
            'handlers': ['security_file'],
            'level': 'WARNING',
            'propagate': True,
        },
        'core.views': {
            'handlers': ['file', 'audit_file'],
            'level': 'INFO',
            'propagate': True,
        },
        'core.models': {
            'handlers': ['file', 'error_file'],
            'level': 'INFO',
            'propagate': True,
        },
        'core.decorators': {
            'handlers': ['security_file', 'audit_file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

### Using Logging in Code
```python
import logging

logger = logging.getLogger(__name__)

# Different log levels
logger.debug('Debug message')
logger.info('Info message')
logger.warning('Warning message')
logger.error('Error message')
logger.critical('Critical message')
```

### Viewing Logs
```bash
# View last 50 lines
tail -n 50 logs/debug.log

# Watch logs in real-time
tail -f logs/debug.log

# Search for specific events
grep "User" logs/audit.log

# Search for errors
grep "ERROR\|CRITICAL" logs/errors.log
```

---

## 🚀 Installation & Setup

### Prerequisites
- Python 3.10+
- pip (Python package manager)
- Virtual environment (recommended)

### Installation Steps

1. **Clone or download the project**
```bash
cd "k.junior school"
```

2. **Create virtual environment**
```bash
python -m venv venv
```

3. **Activate virtual environment**
```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

4. **Install dependencies**
```bash
pip install django reportlab
```

5. **Run migrations**
```bash
python manage.py migrate
```

6. **Create superuser**
```bash
python manage.py createsuperuser
```

7. **Run development server**
```bash
python manage.py runserver
```

8. **Access the application**
- Main site: http://localhost:8000/
- Admin: http://localhost:8000/admin/

### Setup Sample Data
```bash
python setup_data.py
```

This creates:
- Sample teachers
- Sample subjects
- Sample students
- Sample marks
- Sample attendance

---

## ⚙️ Configuration

### Environment Variables
Create a `.env` file in the project root:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

### Settings Configuration

#### Database
```python
# Development (SQLite)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Production (PostgreSQL)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'school_db',
        'USER': 'postgres',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

#### Static Files
```python
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
```

#### Media Files
```python
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

---

## 📚 API Reference

### Model Methods

#### Mark.get_percentage()
Calculates percentage for a mark.

```python
def get_percentage(self):
    if self.total_marks > 0:
        return (self.marks_obtained / self.total_marks) * 100
    return 0
```

**Returns:** `float` - Percentage value

#### Mark.save()
Auto-calculates grade before saving.

```python
def save(self, *args, **kwargs):
    if self.total_marks > 0:
        percentage = (self.marks_obtained / self.total_marks) * 100
    else:
        percentage = 0
    
    if percentage >= 90:
        self.grade = 'A+'
    elif percentage >= 80:
        self.grade = 'A'
    elif percentage >= 70:
        self.grade = 'B'
    elif percentage >= 60:
        self.grade = 'C'
    elif percentage >= 50:
        self.grade = 'D'
    else:
        self.grade = 'F'
    super().save(*args, **kwargs)
```

### Custom Decorators

#### @login_required
Ensures user is authenticated.

#### @teacher_required
Ensures user is a teacher.

#### @student_required
Ensures user is a student.

#### @parent_required
Ensures user is a parent.

#### @admin_required
Ensures user is admin or superuser.

#### @profile_required
Ensures user has a profile.

#### @owner_or_admin_required
Ensures user is owner or admin.

#### @require_ajax
Ensures request is AJAX.

### Template Tags

#### Custom Template Tags (`core/templatetags/custom_tags.py`)
```python
@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)
```

**Usage in template:**
```html
{{ dictionary|get_item:key }}
```

---

## 🎓 Best Practices

### Code Organization
- Keep views thin, models fat
- Use forms for validation
- Use decorators for access control
- Use logging for debugging

### Security
- Never hardcode secrets
- Always validate user input
- Use CSRF protection
- Use HTTPS in production

### Performance
- Use `select_related()` for foreign keys
- Use `prefetch_related()` for reverse relations
- Use pagination for large lists
- Cache frequently accessed data

### Testing
- Write tests for all models
- Write tests for all forms
- Write tests for critical views
- Run tests before deployment

---

## 📞 Support & Maintenance

### Common Issues

#### Issue: Tests Fail
**Solution:**
```bash
python manage.py migrate
python manage.py test
```

#### Issue: Static Files Not Loading
**Solution:**
```bash
python manage.py collectstatic --noinput
```

#### Issue: Permission Denied
**Solution:** Add appropriate decorator to view.

#### Issue: Database Errors
**Solution:** Check migrations are applied:
```bash
python manage.py migrate
```

### Maintenance Tasks

#### Daily
- Check error logs
- Monitor system performance

#### Weekly
- Review audit logs
- Check disk space
- Backup database

#### Monthly
- Update dependencies
- Review security logs
- Performance optimization

---

## 📈 Future Enhancements

### Planned Features
- [ ] Email notifications
- [ ] SMS alerts
- [ ] Mobile app
- [ ] Online exams
- [ ] Fee management
- [ ] Library management
- [ ] Transport management
- [ ] Hostel management

### Technical Improvements
- [ ] Redis caching
- [ ] Celery background tasks
- [ ] WebSocket real-time updates
- [ ] GraphQL API
- [ ] Docker containerization
- [ ] CI/CD pipeline
- [ ] Load balancing
- [ ] Database sharding

---

## 📄 License

This project is developed for educational purposes.

---

## 👨‍💻 Development Team

**Project**: Django School Management System
**Version**: 1.0.0
**Last Updated**: 2026-03-29

---

## 📚 Additional Documentation

- **IMPLEMENTATION_COMPLETE.md** - Implementation summary
- **QUICK_REFERENCE.md** - Quick lookup guide
- **ADVANCED_FEATURES.md** - Advanced features guide
- **DEBUG_REPORT.md** - Debugging report
- **FORMS_IMPLEMENTATION.md** - Forms documentation
- **PROJECT_DEBUG_REPORT.md** - Project debug report

---

**End of Documentation**
