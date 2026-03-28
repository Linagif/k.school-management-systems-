from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg
from .models import UserProfile, Student, Teacher, Subject, Mark, Attendance
from .forms import LoginForm, StudentSignupForm, TeacherSignupForm, ParentSignupForm, MarkForm, FilterAttendanceForm, FilterMarkForm
from datetime import date
from django.contrib.auth.models import User
from decimal import Decimal, InvalidOperation

# Login View
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

# Signup/Register View
def signup_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    user_type = request.GET.get('type', 'student')
    
    # Select appropriate form based on user type
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
            # Create user
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name']
            )
            
            # Create user profile
            UserProfile.objects.create(
                user=user,
                user_type=user_type,
                phone=form.cleaned_data.get('phone', '')
            )
            
            # Create specific profile based on user type
            try:
                if user_type == 'student':
                    Student.objects.create(
                        user=user,
                        admission_number=form.cleaned_data['admission_number'],
                        date_of_birth=form.cleaned_data['date_of_birth'],
                        grade=form.cleaned_data['grade']
                    )
                elif user_type == 'teacher':
                    Teacher.objects.create(
                        user=user,
                        employee_id=form.cleaned_data['employee_id'],
                        specialization=form.cleaned_data['specialization']
                    )
                
                messages.success(request, f'{user_type.capitalize()} account created successfully! Please login.')
                return redirect('login')
            except Exception as e:
                user.delete()
                messages.error(request, f'Error creating profile: {str(e)}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{error}')
    else:
        form = FormClass()
    
    return render(request, 'signup.html', {'form': form, 'user_type': user_type})

# Logout View
def logout_view(request):
    logout(request)
    return redirect('login')

# Dashboard View - redirects based on user type
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
    except UserProfile.DoesNotExist:
        # If user is superuser without profile, redirect to admin
        if request.user.is_superuser:
            return redirect('admin_dashboard')
        messages.error(request, 'User profile not found. Please contact administrator.')
        return redirect('login')

# Admin Dashboard
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

# Admin - View All Students
@login_required
def admin_students(request):
    if not (request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.user_type == 'admin')):
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    students = Student.objects.select_related('user', 'parent').all()
    return render(request, 'admin_students.html', {'students': students})

# Admin - View All Marks
@login_required
def admin_marks(request):
    if not (request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.user_type == 'admin')):
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    marks = Mark.objects.select_related('student__user', 'subject', 'added_by__user').all()
    return render(request, 'admin_marks.html', {'marks': marks})

# Teacher Dashboard
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

# Teacher - View Students
@login_required
def teacher_students(request):
    if not hasattr(request.user, 'profile') or request.user.profile.user_type != 'teacher':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    students = Student.objects.select_related('user').all()
    return render(request, 'teacher_students.html', {'students': students})

# Teacher - Add Marks
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
    subjects = Subject.objects.all()
    
    context = {
        'form': form,
        'students': students,
        'subjects': subjects,
    }
    return render(request, 'teacher_add_marks.html', context)

# Teacher - View Marks
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

# Student Dashboard
@login_required
def student_dashboard(request):
    if not hasattr(request.user, 'profile') or request.user.profile.user_type != 'student':
        messages.error(request, 'Access denied. Student privileges required.')
        return redirect('dashboard')
    
    try:
        student = request.user.student_profile
        marks = Mark.objects.filter(student=student).select_related('subject')
        
        # Calculate average percentage correctly
        if marks.exists():
            total_percentage = 0
            for mark in marks:
                total_percentage += mark.get_percentage()
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

# Parent Dashboard
@login_required
def parent_dashboard(request):
    if not hasattr(request.user, 'profile') or request.user.profile.user_type != 'parent':
        messages.error(request, 'Access denied. Parent privileges required.')
        return redirect('dashboard')
    
    children = Student.objects.filter(parent=request.user).select_related('user')
    
    context = {
        'children': children,
    }
    return render(request, 'parent_dashboard.html', context)

# Parent - View Child Marks
@login_required
def parent_view_child_marks(request, student_id):
    if not hasattr(request.user, 'profile') or request.user.profile.user_type != 'parent':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    student = get_object_or_404(Student, id=student_id, parent=request.user)
    marks = Mark.objects.filter(student=student).select_related('subject')
    
    # Calculate average percentage correctly
    if marks.exists():
        total_percentage = 0
        for mark in marks:
            total_percentage += mark.get_percentage()
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

# Teacher - Mark Attendance
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
                student = Student.objects.get(id=student_id)
                Attendance.objects.update_or_create(
                    student=student,
                    date=attendance_date,
                    defaults={
                        'status': status,
                        'remarks': remarks,
                        'marked_by': teacher
                    }
                )
        
        messages.success(request, f'Attendance marked successfully for {attendance_date}!')
        return redirect('teacher_mark_attendance')
    
    students = Student.objects.select_related('user').all()
    
    # Get existing attendance for the selected date
    existing_attendance = {}
    for att in Attendance.objects.filter(date=attendance_date):
        existing_attendance[att.student_id] = att
    
    context = {
        'students': students,
        'attendance_date': attendance_date,
        'existing_attendance': existing_attendance,
    }
    return render(request, 'teacher_mark_attendance.html', context)

# Teacher - View Attendance
@login_required
def teacher_view_attendance(request):
    if not hasattr(request.user, 'profile') or request.user.profile.user_type != 'teacher':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    attendance_records = Attendance.objects.select_related('student__user', 'marked_by__user').order_by('-date')
    
    # Use filter form
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

# Student - View My Attendance
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
    
    # Calculate statistics
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

# Parent - View Child Attendance
@login_required
def parent_view_child_attendance(request, student_id):
    if not hasattr(request.user, 'profile') or request.user.profile.user_type != 'parent':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    student = get_object_or_404(Student, id=student_id, parent=request.user)
    attendance_records = Attendance.objects.filter(student=student).order_by('-date')
    
    # Calculate statistics
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

# Admin - View All Attendance
@login_required
def admin_attendance(request):
    if not (request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.user_type == 'admin')):
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    attendance_records = Attendance.objects.select_related('student__user', 'marked_by__user').order_by('-date')
    
    # Use filter form
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
