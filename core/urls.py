from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('login/', views.login_view, name='login'),
    path('', views.login_view, name='login_root'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Admin URLs
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/students/', views.admin_students, name='admin_students'),
    path('admin/marks/', views.admin_marks, name='admin_marks'),
    
    # Teacher URLs
    path('teacher-dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('teacher/students/', views.teacher_students, name='teacher_students'),
    path('teacher/add-marks/', views.teacher_add_marks, name='teacher_add_marks'),
    path('teacher/view-marks/', views.teacher_view_marks, name='teacher_view_marks'),
    
    # Student URLs
    path('student-dashboard/', views.student_dashboard, name='student_dashboard'),
    
    # Parent URLs
    path('parent-dashboard/', views.parent_dashboard, name='parent_dashboard'),
    path('parent/child/<int:student_id>/marks/', views.parent_view_child_marks, name='parent_view_child_marks'),
    path('parent/child/<int:student_id>/attendance/', views.parent_view_child_attendance, name='parent_view_child_attendance'),

    # Attendance URLs
    path('admin/attendance/', views.admin_attendance, name='admin_attendance'),
    path('teacher/mark-attendance/', views.teacher_mark_attendance, name='teacher_mark_attendance'),
    path('teacher/view-attendance/', views.teacher_view_attendance, name='teacher_view_attendance'),
    path('student/attendance/', views.student_attendance, name='student_attendance'),
]
