"""
Custom decorators for permission checking and access control.
Replaces repetitive permission checks in views with clean, reusable decorators.
"""

from functools import wraps
from django.contrib import messages
from django.shortcuts import redirect
import logging

logger = logging.getLogger(__name__)


def user_type_required(required_user_type):
    """
    Decorator to check if user has required user type.
    
    Usage:
        @login_required
        @user_type_required('teacher')
        def teacher_view(request):
            # View code here
    
    Args:
        required_user_type (str): The required user type ('admin', 'teacher', 'student', 'parent')
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not hasattr(request.user, 'profile'):
                messages.error(request, 'User profile not found. Please contact administrator.')
                logger.warning(f'Access attempt by user without profile: {request.user.username}')
                return redirect('login')
            
            if request.user.profile.user_type != required_user_type:
                messages.error(request, f'Access denied. {required_user_type.capitalize()} privileges required.')
                logger.warning(
                    f'Unauthorized access attempt by {request.user.username} '
                    f'(type: {request.user.profile.user_type}) to {required_user_type} view'
                )
                return redirect('dashboard')
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def admin_required(view_func):
    """
    Decorator to check if user is admin or superuser.
    
    Usage:
        @login_required
        @admin_required
        def admin_view(request):
            # View code here
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        is_admin = (
            request.user.is_superuser or 
            (hasattr(request.user, 'profile') and request.user.profile.user_type == 'admin')
        )
        
        if not is_admin:
            messages.error(request, 'Access denied. Admin privileges required.')
            logger.warning(f'Unauthorized admin access attempt by {request.user.username}')
            return redirect('dashboard')
        
        return view_func(request, *args, **kwargs)
    return wrapper


def teacher_required(view_func):
    """
    Decorator to check if user is a teacher.
    
    Usage:
        @login_required
        @teacher_required
        def teacher_view(request):
            # View code here
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not hasattr(request.user, 'profile') or request.user.profile.user_type != 'teacher':
            messages.error(request, 'Access denied. Teacher privileges required.')
            logger.warning(f'Unauthorized teacher access attempt by {request.user.username}')
            return redirect('dashboard')
        
        return view_func(request, *args, **kwargs)
    return wrapper


def student_required(view_func):
    """
    Decorator to check if user is a student.
    
    Usage:
        @login_required
        @student_required
        def student_view(request):
            # View code here
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not hasattr(request.user, 'profile') or request.user.profile.user_type != 'student':
            messages.error(request, 'Access denied. Student privileges required.')
            logger.warning(f'Unauthorized student access attempt by {request.user.username}')
            return redirect('dashboard')
        
        return view_func(request, *args, **kwargs)
    return wrapper


def parent_required(view_func):
    """
    Decorator to check if user is a parent.
    
    Usage:
        @login_required
        @parent_required
        def parent_view(request):
            # View code here
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not hasattr(request.user, 'profile') or request.user.profile.user_type != 'parent':
            messages.error(request, 'Access denied. Parent privileges required.')
            logger.warning(f'Unauthorized parent access attempt by {request.user.username}')
            return redirect('dashboard')
        
        return view_func(request, *args, **kwargs)
    return wrapper


def profile_required(view_func):
    """
    Decorator to ensure user has a profile.
    
    Usage:
        @login_required
        @profile_required
        def any_view(request):
            # View code here - user.profile is guaranteed to exist
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not hasattr(request.user, 'profile'):
            messages.error(request, 'User profile not found. Please contact administrator.')
            logger.warning(f'Access attempt by user without profile: {request.user.username}')
            return redirect('login')
        
        return view_func(request, *args, **kwargs)
    return wrapper


def owner_or_admin_required(view_func):
    """
    Decorator to check if user owns the resource or is admin.
    
    The view function MUST have a 'pk' or 'student_id' parameter.
    
    Usage:
        @login_required
        @owner_or_admin_required
        def edit_student(request, pk):
            # User must be the student or admin
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        from .models import Student
        
        # Get student ID from kwargs
        student_id = kwargs.get('student_id') or kwargs.get('pk')
        
        if not student_id:
            messages.error(request, 'Invalid request.')
            return redirect('dashboard')
        
        try:
            student = Student.objects.get(id=student_id)
            is_owner = request.user == student.user
            is_admin = request.user.is_superuser or (
                hasattr(request.user, 'profile') and request.user.profile.user_type == 'admin'
            )
            
            if not (is_owner or is_admin):
                messages.error(request, 'You do not have permission to access this resource.')
                logger.warning(
                    f'Unauthorized access attempt by {request.user.username} '
                    f'to student {student_id}'
                )
                return redirect('dashboard')
        except Student.DoesNotExist:
            messages.error(request, 'Student not found.')
            return redirect('dashboard')
        
        return view_func(request, *args, **kwargs)
    return wrapper


def require_ajax(view_func):
    """
    Decorator to require request to be AJAX.
    
    Usage:
        @require_ajax
        def api_endpoint(request):
            # This view only accepts AJAX requests
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            messages.error(request, 'Invalid request.')
            logger.warning(f'Non-AJAX request to AJAX-only endpoint by {request.user.username}')
            return redirect('dashboard')
        
        return view_func(request, *args, **kwargs)
    return wrapper
