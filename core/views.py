from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.db import transaction
from django.db.models import Avg, Count, Q
from django.utils import timezone
from .models import UserProfile, Student, Teacher, Subject, Mark, Attendance
from .forms import LoginForm, StudentSignupForm, TeacherSignupForm, ParentSignupForm, MarkForm, FilterAttendanceForm, FilterMarkForm
from datetime import date, datetime
from django.contrib.auth.models import User
from decimal import Decimal, InvalidOperation
import io
from reportlab.lib import colors  # type: ignore[reportMissingModuleSource]
from reportlab.lib.pagesizes import letter, A4  # type: ignore[reportMissingModuleSource]
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle  # type: ignore[reportMissingModuleSource]
from reportlab.lib.units import inch, cm  # type: ignore[reportMissingModuleSource]
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image  # type: ignore[reportMissingModuleSource]
from reportlab.lib.enums import TA_CENTER, TA_RIGHT  # type: ignore[reportMissingModuleSource]
from reportlab.graphics.shapes import Drawing, Line  # type: ignore[reportMissingModuleSource]
from reportlab.graphics.charts.barcharts import VerticalBarChart  # type: ignore[reportMissingModuleSource]
from reportlab.graphics.charts.piecharts import Pie  # type: ignore[reportMissingModuleSource]
from reportlab.graphics import renderPDF  # type: ignore[reportMissingModuleSource]


# ==================== AUTH VIEWS ====================

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid username or password')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})


def signup_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    user_type = request.GET.get('type', 'student')

    if user_type == 'teacher':
        FormClass = TeacherSignupForm
    elif user_type == 'parent':
        FormClass = ParentSignupForm
    else:
        FormClass = StudentSignupForm
        user_type = 'student'

    if request.method == 'POST':
        form = FormClass(request.POST)
        if form.is_valid():
            try:
                # FIX: wrap all DB writes in a single atomic block so any
                # failure rolls back everything — no orphaned User rows.
                with transaction.atomic():
                    user_kwargs = {
                        'password': form.cleaned_data['password'],
                        'first_name': form.cleaned_data['first_name'],
                        'last_name': form.cleaned_data['last_name'],
                    }

                    if user_type == 'student':
                        user_kwargs['username'] = form.cleaned_data['admission_number']
                    elif user_type == 'teacher':
                        user_kwargs['username'] = form.cleaned_data['employee_id']
                    else:
                        if 'username' in form.cleaned_data:
                            user_kwargs['username'] = form.cleaned_data['username']
                        else:
                            messages.error(request, 'Username is required')
                            return render(request, 'signup.html', {'form': form, 'user_type': user_type})

                    if 'email' in form.cleaned_data:
                        user_kwargs['email'] = form.cleaned_data['email']

                    user = User.objects.create_user(**user_kwargs)

                    profile_kwargs = {
                        'user': user,
                        'user_type': user_type,
                    }
                    if 'phone' in form.cleaned_data:
                        profile_kwargs['phone'] = form.cleaned_data.get('phone', '')

                    UserProfile.objects.create(**profile_kwargs)

                    if user_type == 'student':
                        Student.objects.create(
                            user=user,
                            admission_number=form.cleaned_data['admission_number'],
                            grade=form.cleaned_data['grade'],
                        )
                    elif user_type == 'teacher':
                        Teacher.objects.create(
                            user=user,
                            employee_id=form.cleaned_data['employee_id'],
                        )
                    elif user_type == 'parent':
                        # Create child student records if child details are provided
                        # Support up to 2 children
                        for i in range(1, 3):  # child_1, child_2
                            child_name = request.POST.get(f'child_name_{i}', '').strip()
                            child_grade = request.POST.get(f'child_grade_{i}', '').strip()
                            child_admission = request.POST.get(f'child_admission_{i}', '').strip()
                            
                            if child_name and child_grade:
                                # Check if admission number provided (existing student)
                                if child_admission:
                                    # Link existing student to this parent
                                    try:
                                        existing_student = Student.objects.get(admission_number=child_admission)
                                        if existing_student.can_add_parent():
                                            existing_student.parents.add(user)
                                        else:
                                            messages.warning(request, f'Student {child_admission} already has maximum of 2 parents.')
                                    except Student.DoesNotExist:
                                        messages.warning(request, f'Student with admission number {child_admission} not found.')
                                else:
                                    # Generate a unique admission number for the child
                                    import uuid
                                    admission_number = f'CHD-{uuid.uuid4().hex[:8].upper()}'
                                    # Split child name into first and last name
                                    name_parts = child_name.split(' ', 1)
                                    child_first_name = name_parts[0]
                                    child_last_name = name_parts[1] if len(name_parts) > 1 else ''
                                    # Create user for the child
                                    child_user = User.objects.create_user(
                                        username=admission_number,
                                        password=form.cleaned_data['password'],
                                        first_name=child_first_name,
                                        last_name=child_last_name,
                                    )
                                    # Create user profile for the child
                                    UserProfile.objects.create(
                                        user=child_user,
                                        user_type='student',
                                    )
                                    # Create student record linked to parent
                                    student = Student.objects.create(
                                        user=child_user,
                                        admission_number=admission_number,
                                        grade=child_grade,
                                    )
                                    # Add parent to the student
                                    student.parents.add(user)

                messages.success(request, f'{user_type.capitalize()} account created successfully! Please login.')
                return redirect('login')

            except Exception as e:
                if 'username' in str(e).lower():
                    messages.error(request, 'This username/admission number is already taken.')
                elif 'email' in str(e).lower() and user_type != 'parent':
                    messages.error(request, 'This email is already registered. Please use a different one.')
                else:
                    messages.error(request, f'Error creating account: {str(e)}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{error}')
    else:
        form = FormClass()

    return render(request, 'signup.html', {'form': form, 'user_type': user_type})


def logout_view(request):
    logout(request)
    return redirect('login')


# ==================== DASHBOARD ====================

@login_required
def dashboard(request):
    try:
        user_profile = request.user.profile
        user_type = user_profile.user_type

        if user_type == 'admin':
            return redirect('admin_dashboard')
        elif user_type == 'teacher':
            return redirect('teacher_dashboard')
        elif user_type == 'student':
            return redirect('student_dashboard')
        elif user_type == 'parent':
            return redirect('parent_dashboard')
        else:
            messages.error(request, 'Unknown user type. Please contact administrator.')
            return redirect('login')
    except UserProfile.DoesNotExist:
        if request.user.is_superuser:
            return redirect('admin_dashboard')
        messages.error(request, 'User profile not found. Please contact administrator.')
        return redirect('login')
    except Exception:
        messages.error(request, 'An error occurred. Please login again.')
        return redirect('login')


# ==================== ADMIN VIEWS ====================

@login_required
def admin_dashboard(request):
    if not (request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.user_type == 'admin')):
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('dashboard')

    total_students = Student.objects.count()
    total_teachers = Teacher.objects.count()
    total_subjects = Subject.objects.count()
    total_marks = Mark.objects.count()

    recent_marks = Mark.objects.select_related('student__user', 'subject').order_by('-created_at')[:10]

    context = {
        'total_students': total_students,
        'total_teachers': total_teachers,
        'total_subjects': total_subjects,
        'total_marks': total_marks,
        'recent_marks': recent_marks,
    }
    return render(request, 'admin_dashboard.html', context)


@login_required
def admin_students(request):
    if not (request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.user_type == 'admin')):
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    students = Student.objects.select_related('user').prefetch_related('parents').all()
    return render(request, 'admin_students.html', {'students': students})


@login_required
def admin_marks(request):
    if not (request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.user_type == 'admin')):
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    marks = Mark.objects.select_related('student__user', 'subject', 'added_by__user').all()
    return render(request, 'admin_marks.html', {'marks': marks})


# ==================== TEACHER VIEWS ====================

@login_required
def teacher_dashboard(request):
    if not hasattr(request.user, 'profile') or request.user.profile.user_type != 'teacher':
        messages.error(request, 'Access denied. Teacher privileges required.')
        return redirect('dashboard')

    try:
        teacher = request.user.teacher_profile
        subjects = teacher.subjects.all()
        marks_added = Mark.objects.filter(added_by=teacher).count()

        context = {
            'teacher': teacher,
            'subjects': subjects,
            'marks_added': marks_added,
        }
        return render(request, 'teacher_dashboard.html', context)
    except Teacher.DoesNotExist:
        messages.error(request, 'Teacher profile not found.')
        return redirect('login')


@login_required
def teacher_students(request):
    if not hasattr(request.user, 'profile') or request.user.profile.user_type != 'teacher':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    students = Student.objects.select_related('user').all()
    return render(request, 'teacher_students.html', {'students': students})


@login_required
def teacher_add_marks(request):
    if not hasattr(request.user, 'profile') or request.user.profile.user_type != 'teacher':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    try:
        teacher = request.user.teacher_profile
    except Teacher.DoesNotExist:
        messages.error(request, 'Teacher profile not found.')
        return redirect('login')

    if request.method == 'POST':
        form = MarkForm(request.POST)
        if form.is_valid():
            try:
                mark = form.save(commit=False)
                mark.added_by = teacher
                mark.save()
                messages.success(request, 'Marks saved successfully!')
                return redirect('teacher_add_marks')
            except Exception as e:
                messages.error(request, f'Error saving marks: {str(e)}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = MarkForm()

    students = Student.objects.select_related('user').all()
    # FIX: only show subjects this teacher is assigned to, not all subjects.
    subjects = teacher.subjects.all()

    context = {
        'form': form,
        'students': students,
        'subjects': subjects,
    }
    return render(request, 'teacher_add_marks.html', context)


@login_required
def teacher_view_marks(request):
    if not hasattr(request.user, 'profile') or request.user.profile.user_type != 'teacher':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    try:
        teacher = request.user.teacher_profile
        marks = Mark.objects.filter(added_by=teacher).select_related('student__user', 'subject')
    except Teacher.DoesNotExist:
        marks = []

    return render(request, 'teacher_view_marks.html', {'marks': marks})


# ==================== STUDENT VIEWS ====================

@login_required
def student_dashboard(request):
    if not hasattr(request.user, 'profile') or request.user.profile.user_type != 'student':
        messages.error(request, 'Access denied. Student privileges required.')
        return redirect('dashboard')

    try:
        student = request.user.student_profile
        marks = Mark.objects.filter(student=student).select_related('subject')

        if marks.exists():
            total_percentage = sum(mark.get_percentage() for mark in marks)
            avg_percentage = total_percentage / marks.count()
        else:
            avg_percentage = 0

        context = {
            'student': student,
            'marks': marks,
            'avg_percentage': avg_percentage,
        }
        return render(request, 'student_dashboard.html', context)
    except Student.DoesNotExist:
        messages.error(request, 'Student profile not found.')
        return redirect('login')


# ==================== PARENT VIEWS ====================

@login_required
def parent_dashboard(request):
    if not hasattr(request.user, 'profile') or request.user.profile.user_type != 'parent':
        messages.error(request, 'Access denied. Parent privileges required.')
        return redirect('dashboard')

    children = Student.objects.filter(parents=request.user).select_related('user')

    context = {
        'children': children,
    }
    return render(request, 'parent_dashboard.html', context)


@login_required
def parent_view_child_marks(request, student_id):
    if not hasattr(request.user, 'profile') or request.user.profile.user_type != 'parent':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    student = get_object_or_404(Student, id=student_id, parents=request.user)
    marks = Mark.objects.filter(student=student).select_related('subject')

    if marks.exists():
        total_percentage = sum(mark.get_percentage() for mark in marks)
        avg_percentage = total_percentage / marks.count()
    else:
        avg_percentage = 0

    context = {
        'student': student,
        'marks': marks,
        'avg_percentage': avg_percentage,
    }
    return render(request, 'parent_view_marks.html', context)


# ==================== ATTENDANCE VIEWS ====================

@login_required
def teacher_mark_attendance(request):
    if not hasattr(request.user, 'profile') or request.user.profile.user_type != 'teacher':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    try:
        teacher = request.user.teacher_profile
    except Teacher.DoesNotExist:
        messages.error(request, 'Teacher profile not found.')
        return redirect('login')

    attendance_date = request.GET.get('date', str(date.today()))

    if request.method == 'POST':
        attendance_date = request.POST.get('attendance_date')
        students_data = request.POST.getlist('student_ids')

        for student_id in students_data:
            status = request.POST.get(f'status_{student_id}')
            remarks = request.POST.get(f'remarks_{student_id}', '')

            if status:
                # FIX: use get_object_or_404 instead of bare .get() to avoid
                # an unhandled DoesNotExist 500 if a student_id is invalid.
                student = get_object_or_404(Student, id=student_id)
                Attendance.objects.update_or_create(
                    student=student,
                    date=attendance_date,
                    defaults={
                        'status': status,
                        'remarks': remarks,
                        'marked_by': teacher,
                    }
                )

        messages.success(request, f'Attendance marked successfully for {attendance_date}!')
        return redirect('teacher_mark_attendance')

    students = Student.objects.select_related('user').all()

    existing_attendance = {}
    for att in Attendance.objects.filter(date=attendance_date):
        existing_attendance[att.student.id] = att

    context = {
        'students': students,
        'attendance_date': attendance_date,
        'existing_attendance': existing_attendance,
    }
    return render(request, 'teacher_mark_attendance.html', context)


@login_required
def teacher_view_attendance(request):
    if not hasattr(request.user, 'profile') or request.user.profile.user_type != 'teacher':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    attendance_records = Attendance.objects.select_related('student__user', 'marked_by__user').order_by('-date')

    form = FilterAttendanceForm(request.GET or None)
    if form.is_valid():
        if form.cleaned_data.get('student'):
            attendance_records = attendance_records.filter(student=form.cleaned_data['student'])
        if form.cleaned_data.get('status'):
            attendance_records = attendance_records.filter(status=form.cleaned_data['status'])
        if form.cleaned_data.get('date_from'):
            attendance_records = attendance_records.filter(date__gte=form.cleaned_data['date_from'])
        if form.cleaned_data.get('date_to'):
            attendance_records = attendance_records.filter(date__lte=form.cleaned_data['date_to'])

    context = {
        'attendance_records': attendance_records,
        'form': form,
    }
    return render(request, 'teacher_view_attendance.html', context)


@login_required
def student_attendance(request):
    if not hasattr(request.user, 'profile') or request.user.profile.user_type != 'student':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    try:
        student = request.user.student_profile
    except Student.DoesNotExist:
        messages.error(request, 'Student profile not found.')
        return redirect('login')

    attendance_records = Attendance.objects.filter(student=student).order_by('-date')

    total_days = attendance_records.count()
    present_days = attendance_records.filter(status='present').count()
    absent_days = attendance_records.filter(status='absent').count()
    late_days = attendance_records.filter(status='late').count()
    excused_days = attendance_records.filter(status='excused').count()
    attendance_percentage = (present_days / total_days * 100) if total_days > 0 else 0

    context = {
        'attendance_records': attendance_records,
        'total_days': total_days,
        'present_days': present_days,
        'absent_days': absent_days,
        'late_days': late_days,
        'excused_days': excused_days,
        'attendance_percentage': attendance_percentage,
    }
    return render(request, 'student_attendance.html', context)


@login_required
def parent_view_child_attendance(request, student_id):
    if not hasattr(request.user, 'profile') or request.user.profile.user_type != 'parent':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    student = get_object_or_404(Student, id=student_id, parent=request.user)
    attendance_records = Attendance.objects.filter(student=student).order_by('-date')

    total_days = attendance_records.count()
    present_days = attendance_records.filter(status='present').count()
    absent_days = attendance_records.filter(status='absent').count()
    late_days = attendance_records.filter(status='late').count()
    excused_days = attendance_records.filter(status='excused').count()
    attendance_percentage = (present_days / total_days * 100) if total_days > 0 else 0

    context = {
        'student': student,
        'attendance_records': attendance_records,
        'total_days': total_days,
        'present_days': present_days,
        'absent_days': absent_days,
        'late_days': late_days,
        'excused_days': excused_days,
        'attendance_percentage': attendance_percentage,
    }
    return render(request, 'parent_view_attendance.html', context)


@login_required
def admin_attendance(request):
    if not (request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.user_type == 'admin')):
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    attendance_records = Attendance.objects.select_related('student__user', 'marked_by__user').order_by('-date')

    form = FilterAttendanceForm(request.GET or None)
    if form.is_valid():
        if form.cleaned_data.get('student'):
            attendance_records = attendance_records.filter(student=form.cleaned_data['student'])
        if form.cleaned_data.get('status'):
            attendance_records = attendance_records.filter(status=form.cleaned_data['status'])
        if form.cleaned_data.get('date_from'):
            attendance_records = attendance_records.filter(date__gte=form.cleaned_data['date_from'])
        if form.cleaned_data.get('date_to'):
            attendance_records = attendance_records.filter(date__lte=form.cleaned_data['date_to'])

    context = {
        'attendance_records': attendance_records,
        'form': form,
    }
    return render(request, 'admin_attendance.html', context)


# ==================== REPORT CARD ====================

@login_required
def generate_report_card(request, student_id):
    """Generate PDF report card for a student."""

    # FIX: cast student_id to int before comparing with student_profile.id
    # (URL kwargs are strings; .id is an integer — == always returned False before).
    student_id_int = int(student_id)

    is_admin = request.user.is_superuser or (
        hasattr(request.user, 'profile') and request.user.profile.user_type == 'admin'
    )
    is_teacher = hasattr(request.user, 'profile') and request.user.profile.user_type == 'teacher'
    is_own_student = (
        hasattr(request.user, 'profile')
        and request.user.profile.user_type == 'student'
        and hasattr(request.user, 'student_profile')
        and request.user.student_profile.id == student_id_int
    )
    is_parent = (
        hasattr(request.user, 'profile')
        and request.user.profile.user_type == 'parent'
        and Student.objects.filter(id=student_id_int, parent=request.user).exists()
    )

    if not (is_admin or is_teacher or is_own_student or is_parent):
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    student = get_object_or_404(Student.objects.select_related('user', 'parent'), id=student_id_int)

    marks = Mark.objects.filter(student=student).select_related('subject', 'added_by__user')

    attendance_records = Attendance.objects.filter(student=student)
    total_days = attendance_records.count()
    present_days = attendance_records.filter(status='present').count()
    absent_days = attendance_records.filter(status='absent').count()
    late_days = attendance_records.filter(status='late').count()
    excused_days = attendance_records.filter(status='excused').count()
    attendance_percentage = (present_days / total_days * 100) if total_days > 0 else 0

    if marks.exists():
        total_percentage = sum(mark.get_percentage() for mark in marks)
        avg_percentage = total_percentage / marks.count()
    else:
        avg_percentage = 0

    # ---- Build PDF ----
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=30,
        alignment=TA_CENTER,
    )
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#34495e'),
        spaceAfter=12,
        spaceBefore=20,
    )
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=6,
    )
    small_style = ParagraphStyle(
        'CustomSmall',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#7f8c8d'),
        spaceAfter=4,
    )

    elements = []

    # Header
    elements.append(Paragraph("SCHOOL MANAGEMENT SYSTEM", title_style))
    elements.append(Paragraph("Report Card", heading_style))
    elements.append(Spacer(1, 20))

    # Student information
    elements.append(Paragraph("Student Information", heading_style))

    student_data = [
        ['Student Name:', f"{student.user.first_name} {student.user.last_name}"],
        ['Admission Number:', student.admission_number],
        ['Grade:', student.grade],
        ['Date of Birth:', student.date_of_birth.strftime('%B %d, %Y') if student.date_of_birth else 'N/A'],
        ['Parent/Guardian:', ', '.join([f"{p.first_name} {p.last_name}" for p in student.parents.all()]) if student.parents.exists() else 'N/A'],
        ['Report Generated:', datetime.now().strftime('%B %d, %Y at %I:%M %p')],
    ]

    student_table = Table(student_data, colWidths=[2 * inch, 4 * inch])
    student_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#2c3e50')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
    ]))
    elements.append(student_table)
    elements.append(Spacer(1, 20))

    # Academic performance
    elements.append(Paragraph("Academic Performance", heading_style))

    if marks.exists():
        marks_data = [['Subject', 'Term', 'Year', 'Marks Obtained', 'Total Marks', 'Percentage', 'Grade', 'Remarks']]

        for mark in marks:
            marks_data.append([
                mark.subject.name,
                
                
                str(mark.year),
                str(mark.marks_obtained),
                str(mark.total_marks),
                f"{mark.get_percentage():.1f}%",
                mark.grade,
                mark.remarks or '-',
            ])

        marks_table = Table(
            marks_data,
            colWidths=[1.2 * inch, 0.8 * inch, 0.6 * inch, 1 * inch, 1 * inch, 0.9 * inch, 0.7 * inch, 1.5 * inch],
        )
        marks_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ecf0f1')),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#2c3e50')),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (3, 0), (5, -1), 'CENTER'),
        ]))
        elements.append(marks_table)
        elements.append(Spacer(1, 15))

        # Performance summary
        elements.append(Paragraph("Performance Summary", heading_style))

        overall_grade = (
            'A' if avg_percentage >= 90 else
            'B' if avg_percentage >= 80 else
            'C' if avg_percentage >= 70 else
            'D' if avg_percentage >= 60 else
            'F'
        )

        summary_data = [
            ['Total Subjects:', str(marks.count())],
            ['Average Percentage:', f"{avg_percentage:.1f}%"],
            ['Overall Grade:', overall_grade],
        ]

        summary_table = Table(summary_data, colWidths=[2 * inch, 4 * inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#2ecc71')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#27ae60')),
        ]))
        elements.append(summary_table)
    else:
        elements.append(Paragraph("No academic records found.", normal_style))

    elements.append(Spacer(1, 20))

    # Attendance summary
    elements.append(Paragraph("Attendance Summary", heading_style))

    attendance_data = [
        ['Total School Days:', str(total_days)],
        ['Days Present:', str(present_days)],
        ['Days Absent:', str(absent_days)],
        ['Days Late:', str(late_days)],
        ['Days Excused:', str(excused_days)],
        ['Attendance Percentage:', f"{attendance_percentage:.1f}%"],
    ]

    attendance_table = Table(attendance_data, colWidths=[2 * inch, 4 * inch])
    attendance_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#9b59b6')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#8e44ad')),
    ]))
    elements.append(attendance_table)
    elements.append(Spacer(1, 20))

    # Teacher comments
    elements.append(Paragraph("Teacher Comments", heading_style))

    # FIX: exclude marks where added_by is null to avoid "None None: remark" rendering.
    teachers_with_comments = (
        marks
        .filter(remarks__isnull=False, added_by__isnull=False)
        .exclude(remarks='')
        .values_list('added_by__user__first_name', 'added_by__user__last_name', 'remarks')
        .distinct()
    )

    if teachers_with_comments:
        for first_name, last_name, remark in teachers_with_comments:
            elements.append(Paragraph(f"<b>{first_name} {last_name}:</b> {remark}", normal_style))
    else:
        elements.append(Paragraph("No teacher comments available.", normal_style))

    elements.append(Spacer(1, 30))

    # Footer
    elements.append(Paragraph("This is a computer-generated document. No signature required.", small_style))
    elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", small_style))

    doc.build(elements)

    pdf = buffer.getvalue()
    buffer.close()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = (
        f'attachment; filename="report_card_{student.admission_number}_{datetime.now().strftime("%Y%m%d")}.pdf"'
    )
    response.write(pdf)

    return response