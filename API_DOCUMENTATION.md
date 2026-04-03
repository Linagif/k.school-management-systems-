# Django School Management System - API Documentation

## 📋 Table of Contents
1. [Models API](#models-api)
2. [Views API](#views-api)
3. [Forms API](#forms-api)
4. [Decorators API](#decorators-api)
5. [Template Tags API](#template-tags-api)
6. [URL Patterns](#url-patterns)

---

## 📊 Models API

### UserProfile Model

#### Fields
| Field | Type | Description |
|-------|------|-------------|
| `user` | OneToOneField | Link to Django User model |
| `user_type` | CharField | Role: admin, teacher, student, parent |
| `phone` | CharField | Contact number (optional) |
| `address` | TextField | Physical address (optional) |

#### Methods
```python
def __str__(self):
    """Returns string representation"""
    return f"{self.user.username} - {self.user_type}"
```

#### Usage Example
```python
from core.models import UserProfile
from django.contrib.auth.models import User

# Get user profile
user = User.objects.get(username='john')
profile = user.profile

# Check user type
if profile.user_type == 'teacher':
    print("User is a teacher")
```

---

### Student Model

#### Fields
| Field | Type | Description |
|-------|------|-------------|
| `user` | OneToOneField | Link to Django User model |
| `admission_number` | CharField | Unique student identifier |
| `date_of_birth` | DateField | Student's birth date (optional) |
| `grade` | CharField | Current grade/class |
| `parent` | ForeignKey | Link to parent User (optional) |

#### Methods
```python
def __str__(self):
    """Returns string representation"""
    return f"{self.user.get_full_name()} - {self.admission_number}"
```

#### Usage Example
```python
from core.models import Student

# Get all students
students = Student.objects.all()

# Get student by admission number
student = Student.objects.get(admission_number='STU001')

# Get student's marks
marks = student.marks.all()

# Get student's attendance
attendance = student.attendance.all()

# Get student's parent
parent = student.parent
```

#### QuerySet Methods
```python
# Filter by grade
grade_10_students = Student.objects.filter(grade='10A')

# Get students with parent
students_with_parent = Student.objects.filter(parent__isnull=False)

# Search by name
students = Student.objects.filter(
    user__first_name__icontains='john'
)
```

---

### Teacher Model

#### Fields
| Field | Type | Description |
|-------|------|-------------|
| `user` | OneToOneField | Link to Django User model |
| `employee_id` | CharField | Unique teacher identifier |
| `specialization` | CharField | Subject specialization (optional) |
| `date_joined` | DateField | Employment start date (auto) |

#### Methods
```python
def __str__(self):
    """Returns string representation"""
    return f"{self.user.get_full_name()} - {self.employee_id}"
```

#### Usage Example
```python
from core.models import Teacher

# Get all teachers
teachers = Teacher.objects.all()

# Get teacher by employee ID
teacher = Teacher.objects.get(employee_id='TCH001')

# Get teacher's subjects
subjects = teacher.subjects.all()

# Get marks added by teacher
marks_added = teacher.marks_added.all()
```

---

### Subject Model

#### Fields
| Field | Type | Description |
|-------|------|-------------|
| `name` | CharField | Subject name |
| `code` | CharField | Unique subject code |
| `description` | TextField | Subject description (optional) |
| `teacher` | ForeignKey | Assigned teacher (optional) |

#### Methods
```python
def __str__(self):
    """Returns string representation"""
    return f"{self.name} ({self.code})"
```

#### Usage Example
```python
from core.models import Subject

# Get all subjects
subjects = Subject.objects.all()

# Get subject by code
subject = Subject.objects.get(code='MATH101')

# Get subject's teacher
teacher = subject.teacher

# Get all marks for subject
marks = subject.marks.all()
```

---

### Mark Model

#### Fields
| Field | Type | Description |
|-------|------|-------------|
| `student` | ForeignKey | Student reference |
| `subject` | ForeignKey | Subject reference |
| `term` | CharField | Term: 1, 2, or 3 |
| `year` | IntegerField | Academic year |
| `marks_obtained` | DecimalField | Marks achieved |
| `total_marks` | DecimalField | Maximum marks (default: 100) |
| `grade` | CharField | Auto-calculated grade |
| `remarks` | TextField | Additional notes (optional) |
| `added_by` | ForeignKey | Teacher who added marks |
| `created_at` | DateTimeField | Creation timestamp (auto) |
| `updated_at` | DateTimeField | Update timestamp (auto) |

#### Methods

##### `get_percentage()`
Calculates percentage for the mark.

```python
def get_percentage(self):
    """
    Calculate percentage of marks obtained.
    
    Returns:
        float: Percentage value (0-100)
    """
    if self.total_marks > 0:
        return (self.marks_obtained / self.total_marks) * 100
    return 0
```

**Usage:**
```python
mark = Mark.objects.get(id=1)
percentage = mark.get_percentage()
print(f"Percentage: {percentage:.2f}%")
```

##### `save()`
Auto-calculates grade before saving.

```python
def save(self, *args, **kwargs):
    """
    Override save to auto-calculate grade.
    
    Grade Scale:
    - A+: 90-100%
    - A: 80-89%
    - B: 70-79%
    - C: 60-69%
    - D: 50-59%
    - F: Below 50%
    """
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

##### `__str__()`
Returns string representation.

```python
def __str__(self):
    return f"{self.student.user.get_full_name()} - {self.subject.name} - Term {self.term}/{self.year}"
```

#### Meta Options
```python
class Meta:
    unique_together = ['student', 'subject', 'term', 'year']
    ordering = ['-year', '-term', 'subject']
```

#### Usage Example
```python
from core.models import Mark, Student, Subject, Teacher
from decimal import Decimal

# Create a mark
student = Student.objects.get(admission_number='STU001')
subject = Subject.objects.get(code='MATH101')
teacher = Teacher.objects.get(employee_id='TCH001')

mark = Mark.objects.create(
    student=student,
    subject=subject,
    term='1',
    year=2026,
    marks_obtained=Decimal('85'),
    total_marks=Decimal('100'),
    added_by=teacher
)

# Grade is auto-calculated
print(mark.grade)  # Output: 'A'

# Get percentage
print(mark.get_percentage())  # Output: 85.0
```

#### QuerySet Methods
```python
# Get marks for a student
student_marks = Mark.objects.filter(student=student)

# Get marks for a subject
subject_marks = Mark.objects.filter(subject=subject)

# Get marks by term
term_marks = Mark.objects.filter(term='1', year=2026)

# Get marks added by teacher
teacher_marks = Mark.objects.filter(added_by=teacher)

# Get marks with related data (optimized)
marks = Mark.objects.select_related(
    'student__user',
    'subject',
    'added_by__user'
).all()

# Calculate average percentage
from django.db.models import Avg
avg = Mark.objects.filter(student=student).aggregate(
    avg_percentage=Avg('marks_obtained') / Avg('total_marks') * 100
)
```

---

### Attendance Model

#### Fields
| Field | Type | Description |
|-------|------|-------------|
| `student` | ForeignKey | Student reference |
| `date` | DateField | Attendance date |
| `status` | CharField | Status: present, absent, late, excused |
| `remarks` | TextField | Additional notes (optional) |
| `marked_by` | ForeignKey | Teacher who marked attendance |
| `created_at` | DateTimeField | Creation timestamp (auto) |
| `updated_at` | DateTimeField | Update timestamp (auto) |

#### Status Choices
```python
STATUS_CHOICES = (
    ('present', 'Present'),
    ('absent', 'Absent'),
    ('late', 'Late'),
    ('excused', 'Excused'),
)
```

#### Methods
```python
def __str__(self):
    """Returns string representation"""
    return f"{self.student.user.get_full_name()} - {self.date} - {self.status}"
```

#### Meta Options
```python
class Meta:
    unique_together = ['student', 'date']
    ordering = ['-date', 'student']
    verbose_name_plural = 'Attendance'
```

#### Usage Example
```python
from core.models import Attendance, Student, Teacher
from datetime import date

# Mark attendance
student = Student.objects.get(admission_number='STU001')
teacher = Teacher.objects.get(employee_id='TCH001')

attendance = Attendance.objects.create(
    student=student,
    date=date.today(),
    status='present',
    remarks='On time',
    marked_by=teacher
)

# Update or create attendance
Attendance.objects.update_or_create(
    student=student,
    date=date.today(),
    defaults={
        'status': 'late',
        'remarks': 'Arrived 10 minutes late',
        'marked_by': teacher
    }
)
```

#### QuerySet Methods
```python
# Get attendance for a student
student_attendance = Attendance.objects.filter(student=student)

# Get attendance for a date
date_attendance = Attendance.objects.filter(date=date.today())

# Get attendance by status
present_records = Attendance.objects.filter(status='present')

# Get attendance marked by teacher
teacher_attendance = Attendance.objects.filter(marked_by=teacher)

# Get attendance with related data (optimized)
attendance = Attendance.objects.select_related(
    'student__user',
    'marked_by__user'
).all()

# Calculate attendance statistics
from django.db.models import Count
stats = Attendance.objects.filter(student=student).aggregate(
    total=Count('id'),
    present=Count('id', filter=models.Q(status='present')),
    absent=Count('id', filter=models.Q(status='absent')),
    late=Count('id', filter=models.Q(status='late')),
    excused=Count('id', filter=models.Q(status='excused'))
)
```

---

## 🎛️ Views API

### Authentication Views

#### `login_view(request)`
Handles user authentication.

**Method:** GET, POST

**Parameters:**
- `request`: HttpRequest object

**Returns:** HttpResponse

**Template:** `login.html`

**Context:**
- `form`: LoginForm instance

**Example:**
```python
# URL: /login/
# GET: Display login form
# POST: Authenticate user
```

---

#### `signup_view(request)`
Handles user registration.

**Method:** GET, POST

**Parameters:**
- `request`: HttpRequest object
- `type` (GET parameter): User type (student, teacher, parent)

**Returns:** HttpResponse

**Template:** `signup.html`

**Context:**
- `form`: Role-specific signup form
- `user_type`: Selected user type

**Example:**
```python
# URL: /signup/?type=student
# GET: Display student signup form
# POST: Create student account
```

---

#### `logout_view(request)`
Logs out user.

**Method:** GET

**Parameters:**
- `request`: HttpRequest object

**Returns:** HttpResponseRedirect

**Example:**
```python
# URL: /logout/
# Redirects to login page
```

---

### Dashboard Views

#### `dashboard(request)`
Role-based dashboard redirect.

**Method:** GET

**Authentication:** Required

**Returns:** HttpResponseRedirect

**Logic:**
1. Check user profile
2. Determine user type
3. Redirect to appropriate dashboard

**Example:**
```python
# URL: /dashboard/
# Redirects to:
# - /admin-dashboard/ for admins
# - /teacher-dashboard/ for teachers
# - /student-dashboard/ for students
# - /parent-dashboard/ for parents
```

---

#### `admin_dashboard(request)`
Admin dashboard with statistics.

**Method:** GET

**Authentication:** Required (Admin only)

**Template:** `admin_dashboard.html`

**Context:**
- `total_students`: Count of all students
- `total_teachers`: Count of all teachers
- `total_subjects`: Count of all subjects
- `total_marks`: Count of all marks
- `recent_marks`: Last 10 marks added

**Example:**
```python
# URL: /admin-dashboard/
# Displays system-wide statistics
```

---

#### `teacher_dashboard(request)`
Teacher dashboard with subject information.

**Method:** GET

**Authentication:** Required (Teacher only)

**Template:** `teacher_dashboard.html`

**Context:**
- `teacher`: Teacher object
- `subjects`: Assigned subjects
- `marks_added`: Count of marks added

**Example:**
```python
# URL: /teacher-dashboard/
# Displays teacher-specific information
```

---

#### `student_dashboard(request)`
Student dashboard with performance metrics.

**Method:** GET

**Authentication:** Required (Student only)

**Template:** `student_dashboard.html`

**Context:**
- `student`: Student object
- `marks`: All marks with subjects
- `avg_percentage`: Calculated average percentage

**Example:**
```python
# URL: /student-dashboard/
# Displays student performance
```

---

#### `parent_dashboard(request)`
Parent dashboard with children information.

**Method:** GET

**Authentication:** Required (Parent only)

**Template:** `parent_dashboard.html`

**Context:**
- `children`: List of linked students

**Example:**
```python
# URL: /parent-dashboard/
# Displays linked children
```

---

### Mark Management Views

#### `teacher_add_marks(request)`
Form for adding student marks.

**Method:** GET, POST

**Authentication:** Required (Teacher only)

**Template:** `teacher_add_marks.html`

**Context:**
- `form`: MarkForm instance
- `students`: All students
- `subjects`: Teacher's assigned subjects

**Example:**
```python
# URL: /teacher/add-marks/
# GET: Display mark entry form
# POST: Save marks to database
```

---

#### `teacher_view_marks(request)`
Displays marks added by teacher.

**Method:** GET

**Authentication:** Required (Teacher only)

**Template:** `teacher_view_marks.html`

**Context:**
- `marks`: Marks added by current teacher

**Example:**
```python
# URL: /teacher/view-marks/
# Displays marks added by teacher
```

---

#### `admin_marks(request)`
Displays all marks in system.

**Method:** GET

**Authentication:** Required (Admin only)

**Template:** `admin_marks.html`

**Context:**
- `marks`: All marks with related data

**Example:**
```python
# URL: /admin/marks/
# Displays all marks in system
```

---

### Attendance Management Views

#### `teacher_mark_attendance(request)`
Form for marking student attendance.

**Method:** GET, POST

**Authentication:** Required (Teacher only)

**Template:** `teacher_mark_attendance.html`

**Context:**
- `students`: All students
- `attendance_date`: Selected date
- `existing_attendance`: Existing attendance records

**Example:**
```python
# URL: /teacher/mark-attendance/
# GET: Display attendance form
# POST: Save attendance records
```

---

#### `teacher_view_attendance(request)`
Displays attendance records with filtering.

**Method:** GET

**Authentication:** Required (Teacher only)

**Template:** `teacher_view_attendance.html`

**Context:**
- `attendance_records`: Filtered attendance records
- `form`: FilterAttendanceForm instance

**Query Parameters:**
- `student`: Filter by student ID
- `status`: Filter by status
- `date_from`: Filter from date
- `date_to`: Filter to date

**Example:**
```python
# URL: /teacher/view-attendance/
# URL: /teacher/view-attendance/?student=1&status=present
# Displays attendance records
```

---

#### `student_attendance(request)`
Displays student's attendance records.

**Method:** GET

**Authentication:** Required (Student only)

**Template:** `student_attendance.html`

**Context:**
- `attendance_records`: All attendance records
- `total_days`: Total days recorded
- `present_days`: Days present
- `absent_days`: Days absent
- `late_days`: Days late
- `excused_days`: Days excused
- `attendance_percentage`: Calculated percentage

**Example:**
```python
# URL: /student/attendance/
# Displays student attendance with statistics
```

---

#### `parent_view_child_attendance(request, student_id)`
Displays child's attendance for parent.

**Method:** GET

**Authentication:** Required (Parent only)

**Parameters:**
- `student_id`: ID of the student

**Template:** `parent_view_attendance.html`

**Context:**
- `student`: Student object
- `attendance_records`: Attendance records
- `total_days`: Total days recorded
- `present_days`: Days present
- `absent_days`: Days absent
- `late_days`: Days late
- `excused_days`: Days excused
- `attendance_percentage`: Calculated percentage

**Example:**
```python
# URL: /parent/child/1/attendance/
# Displays child attendance for parent
```

---

### Report Generation Views

#### `generate_report_card(request, student_id=None)`
Generates PDF report card.

**Method:** GET

**Authentication:** Required

**Parameters:**
- `student_id` (optional): ID of the student

**Returns:** PDF file download

**Example:**
```python
# URL: /student/report-card/
# Generates report card for current student

# URL: /parent/child/1/report-card/
# Generates report card for child (parent only)
```

---

## 📝 Forms API

### LoginForm

#### Fields
```python
username = forms.CharField(max_length=150)
password = forms.CharField(widget=forms.PasswordInput)
```

#### Usage
```python
from core.forms import LoginForm

form = LoginForm(request.POST)
if form.is_valid():
    username = form.cleaned_data['username']
    password = form.cleaned_data['password']
```

---

### StudentSignupForm

#### Fields
```python
first_name = forms.CharField(max_length=30)
last_name = forms.CharField(max_length=30)
admission_number = forms.CharField(max_length=20)
grade = forms.CharField(max_length=10)
password = forms.CharField(widget=forms.PasswordInput)
confirm_password = forms.CharField(widget=forms.PasswordInput)
```

#### Validation
- Passwords must match
- Admission number must be unique

#### Usage
```python
from core.forms import StudentSignupForm

form = StudentSignupForm(request.POST)
if form.is_valid():
    # Create student account
    pass
```

---

### TeacherSignupForm

#### Fields
```python
first_name = forms.CharField(max_length=30)
last_name = forms.CharField(max_length=30)
employee_id = forms.CharField(max_length=20)
email = forms.EmailField()
password = forms.CharField(widget=forms.PasswordInput)
confirm_password = forms.CharField(widget=forms.PasswordInput)
```

#### Validation
- Passwords must match
- Employee ID must be unique
- Email must be unique

---

### ParentSignupForm

#### Fields
```python
first_name = forms.CharField(max_length=30)
last_name = forms.CharField(max_length=30)
username = forms.CharField(max_length=150)
email = forms.EmailField()
phone = forms.CharField(max_length=15, required=False)
password = forms.CharField(widget=forms.PasswordInput)
confirm_password = forms.CharField(widget=forms.PasswordInput)
```

#### Validation
- Passwords must match
- Username must be unique
- Email must be unique

---

### MarkForm

#### Fields
```python
student = forms.ModelChoiceField(queryset=Student.objects.all())
subject = forms.ModelChoiceField(queryset=Subject.objects.all())
term = forms.ChoiceField(choices=Mark.TERM_CHOICES)
year = forms.IntegerField()
marks_obtained = forms.DecimalField(max_digits=5, decimal_places=2)
total_marks = forms.DecimalField(max_digits=5, decimal_places=2)
remarks = forms.CharField(widget=forms.Textarea, required=False)
```

#### Validation
- Marks obtained cannot exceed total marks
- Total marks must be greater than 0

#### Usage
```python
from core.forms import MarkForm

form = MarkForm(request.POST)
if form.is_valid():
    mark = form.save(commit=False)
    mark.added_by = teacher
    mark.save()
```

---

### FilterAttendanceForm

#### Fields
```python
student = forms.ModelChoiceField(queryset=Student.objects.all(), required=False)
status = forms.ChoiceField(choices=[('', 'All')] + list(Attendance.STATUS_CHOICES), required=False)
date_from = forms.DateField(required=False)
date_to = forms.DateField(required=False)
```

#### Usage
```python
from core.forms import FilterAttendanceForm

form = FilterAttendanceForm(request.GET)
if form.is_valid():
    if form.cleaned_data['student']:
        attendance = attendance.filter(student=form.cleaned_data['student'])
    if form.cleaned_data['status']:
        attendance = attendance.filter(status=form.cleaned_data['status'])
```

---

### FilterMarkForm

#### Fields
```python
student = forms.ModelChoiceField(queryset=Student.objects.all(), required=False)
subject = forms.ModelChoiceField(queryset=Subject.objects.all(), required=False)
term = forms.ChoiceField(choices=[('', 'All')] + list(Mark.TERM_CHOICES), required=False)
year = forms.IntegerField(required=False)
```

---

## 🔐 Decorators API

### @login_required
Ensures user is authenticated.

```python
from django.contrib.auth.decorators import login_required

@login_required
def my_view(request):
    pass
```

---

### @teacher_required
Ensures user is a teacher.

```python
from core.decorators import teacher_required
from django.contrib.auth.decorators import login_required

@login_required
@teacher_required
def teacher_view(request):
    pass
```

---

### @student_required
Ensures user is a student.

```python
from core.decorators import student_required
from django.contrib.auth.decorators import login_required

@login_required
@student_required
def student_view(request):
    pass
```

---

### @parent_required
Ensures user is a parent.

```python
from core.decorators import parent_required
from django.contrib.auth.decorators import login_required

@login_required
@parent_required
def parent_view(request):
    pass
```

---

### @admin_required
Ensures user is admin or superuser.

```python
from core.decorators import admin_required
from django.contrib.auth.decorators import login_required

@login_required
@admin_required
def admin_view(request):
    pass
```

---

### @profile_required
Ensures user has a profile.

```python
from core.decorators import profile_required
from django.contrib.auth.decorators import login_required

@login_required
@profile_required
def profile_view(request):
    pass
```

---

### @owner_or_admin_required
Ensures user is owner or admin.

```python
from core.decorators import owner_or_admin_required
from django.contrib.auth.decorators import login_required

@login_required
@owner_or_admin_required
def edit_student(request, pk):
    pass
```

---

### @require_ajax
Ensures request is AJAX.

```python
from core.decorators import require_ajax

@require_ajax
def api_endpoint(request):
    pass
```

---

## 🏷️ Template Tags API

### Custom Template Tags

#### `get_item`
Gets item from dictionary by key.

**File:** `core/templatetags/custom_tags.py`

**Usage:**
```html
{% load custom_tags %}

{{ dictionary|get_item:key }}
```

**Example:**
```html
{% load custom_tags %}

{% for student in students %}
    {{ attendance|get_item:student.id }}
{% endfor %}
```

---

## 🔗 URL Patterns

### Authentication URLs
```python
path('login/', views.login_view, name='login'),
path('', views.login_view, name='login_root'),
path('signup/', views.signup_view, name='signup'),
path('logout/', views.logout_view, name='logout'),
path('dashboard/', views.dashboard, name='dashboard'),
```

### Admin URLs
```python
path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
path('admin/students/', views.admin_students, name='admin_students'),
path('admin/marks/', views.admin_marks, name='admin_marks'),
path('admin/attendance/', views.admin_attendance, name='admin_attendance'),
```

### Teacher URLs
```python
path('teacher-dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
path('teacher/students/', views.teacher_students, name='teacher_students'),
path('teacher/add-marks/', views.teacher_add_marks, name='teacher_add_marks'),
path('teacher/view-marks/', views.teacher_view_marks, name='teacher_view_marks'),
path('teacher/mark-attendance/', views.teacher_mark_attendance, name='teacher_mark_attendance'),
path('teacher/view-attendance/', views.teacher_view_attendance, name='teacher_view_attendance'),
```

### Student URLs
```python
path('student-dashboard/', views.student_dashboard, name='student_dashboard'),
path('student/attendance/', views.student_attendance, name='student_attendance'),
path('student/report-card/', views.generate_report_card, name='student_report_card'),
```

### Parent URLs
```python
path('parent-dashboard/', views.parent_dashboard, name='parent_dashboard'),
path('parent/child/<int:student_id>/marks/', views.parent_view_child_marks, name='parent_view_child_marks'),
path('parent/child/<int:student_id>/attendance/', views.parent_view_child_attendance, name='parent_view_child_attendance'),
path('parent/child/<int:student_id>/report-card/', views.generate_report_card, name='parent_child_report_card'),
```

---

## 📊 QuerySet Examples

### Common Queries

#### Get all students with their user data
```python
students = Student.objects.select_related('user').all()
```

#### Get marks with related data
```python
marks = Mark.objects.select_related(
    'student__user',
    'subject',
    'added_by__user'
).all()
```

#### Get attendance with related data
```python
attendance = Attendance.objects.select_related(
    'student__user',
    'marked_by__user'
).all()
```

#### Calculate average percentage
```python
from django.db.models import Avg, F

avg = Mark.objects.filter(student=student).aggregate(
    avg_percentage=Avg(F('marks_obtained') / F('total_marks') * 100)
)
```

#### Get attendance statistics
```python
from django.db.models import Count, Q

stats = Attendance.objects.filter(student=student).aggregate(
    total=Count('id'),
    present=Count('id', filter=Q(status='present')),
    absent=Count('id', filter=Q(status='absent')),
    late=Count('id', filter=Q(status='late')),
    excused=Count('id', filter=Q(status='excused'))
)
```

#### Search students by name
```python
students = Student.objects.filter(
    Q(user__first_name__icontains='john') |
    Q(user__last_name__icontains='john')
)
```

#### Get marks by term and year
```python
marks = Mark.objects.filter(term='1', year=2026)
```

#### Get teacher's subjects
```python
teacher = Teacher.objects.get(employee_id='TCH001')
subjects = teacher.subjects.all()
```

#### Get student's parent
```python
student = Student.objects.get(admission_number='STU001')
parent = student.parent
```

---

## 🔧 Utility Functions

### Atomic Transactions
```python
from django.db import transaction

try:
    with transaction.atomic():
        # All database operations here
        # If any fail, all are rolled back
        user = User.objects.create_user(**user_kwargs)
        UserProfile.objects.create(**profile_kwargs)
        Student.objects.create(**student_kwargs)
except Exception as e:
    # Handle error
    pass
```

### Get Object or 404
```python
from django.shortcuts import get_object_or_404

student = get_object_or_404(Student, id=student_id)
```

### Redirect with Message
```python
from django.contrib import messages
from django.shortcuts import redirect

messages.success(request, 'Operation successful!')
return redirect('dashboard')
```

---

**End of API Documentation**
