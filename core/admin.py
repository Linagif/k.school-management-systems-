from django.contrib import admin
from .models import UserProfile, Student, Teacher, Subject, Mark, Attendance

# ==================== ADMIN CUSTOMIZATION ====================

admin.site.site_header = "School Management System Admin"
admin.site.site_title = "School Management"
admin.site.index_title = "Dashboard"


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Enhanced UserProfile admin with filters and search"""
    list_display = ['user', 'user_type', 'phone', 'created_indicator']
    list_filter = ['user_type', 'user__is_active']
    search_fields = ['user__username', 'user__email', 'user__first_name', 'user__last_name', 'phone']
    readonly_fields = ['user', 'created_at'] if hasattr(UserProfile, 'created_at') else ['user']
    
    def created_indicator(self, obj):
        """Display user active status"""
        return "✓ Active" if obj.user.is_active else "✗ Inactive"
    created_indicator.short_description = 'Status'


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    """Enhanced Student admin with full details"""
    list_display = ['get_full_name', 'admission_number', 'grade', 'get_parents', 'date_of_birth_short']
    list_filter = ['grade', 'date_of_birth', 'user__is_active']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'admission_number']
    readonly_fields = ['user', 'admission_number']
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'admission_number')
        }),
        ('Academic Information', {
            'fields': ('grade', 'date_of_birth')
        }),
        ('Parent Information', {
            'fields': ('parents',)
        }),
    )
    
    def get_full_name(self, obj):
        return obj.user.get_full_name()
    get_full_name.short_description = 'Student Name'
    get_full_name.admin_order_field = 'user__first_name'
    
    def get_parents(self, obj):
        return ", ".join([p.get_full_name() for p in obj.parents.all()])
    get_parents.short_description = 'Parents'
    
    def date_of_birth_short(self, obj):
        return obj.date_of_birth.strftime('%Y-%m-%d')
    date_of_birth_short.short_description = 'DOB'


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    """Enhanced Teacher admin with detailed info"""
    list_display = ['get_full_name', 'employee_id', 'specialization', 'date_joined', 'subjects_count']
    list_filter = ['specialization', 'date_joined', 'user__is_active']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'employee_id', 'specialization']
    readonly_fields = ['user', 'employee_id', 'date_joined']
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'employee_id')
        }),
        ('Professional Information', {
            'fields': ('specialization', 'date_joined')
        }),
    )
    
    def get_full_name(self, obj):
        return obj.user.get_full_name()
    get_full_name.short_description = 'Teacher Name'
    get_full_name.admin_order_field = 'user__first_name'
    
    def subjects_count(self, obj):
        return obj.subjects.count()
    subjects_count.short_description = 'Subjects'


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    """Enhanced Subject admin"""
    list_display = ['name', 'code', 'teacher', 'marks_count']
    list_filter = ['teacher']
    search_fields = ['name', 'code', 'description']
    readonly_fields = ['code']
    fieldsets = (
        ('Subject Information', {
            'fields': ('name', 'code')
        }),
        ('Details', {
            'fields': ('description', 'teacher'),
            'classes': ('collapse',)
        }),
    )
    
    def marks_count(self, obj):
        return obj.marks.count()
    marks_count.short_description = 'Total Marks Entered'


@admin.register(Mark)
class MarkAdmin(admin.ModelAdmin):
    """Enhanced Mark admin with filtering and display options"""
    list_display = ['get_student_name', 'subject', 'term', 'year', 'marks_display', 'grade', 'added_by_short']
    list_filter = ['term', 'year', 'subject', 'grade', 'created_at']
    search_fields = ['student__user__first_name', 'student__user__last_name', 'student__admission_number', 'subject__name']
    readonly_fields = ['grade', 'created_at', 'updated_at', 'percentage_display']
    fieldsets = (
        ('Student & Subject', {
            'fields': ('student', 'subject')
        }),
        ('Academic Term', {
            'fields': ('term', 'year')
        }),
        ('Marks Information', {
            'fields': ('marks_obtained', 'total_marks', 'percentage_display', 'grade')
        }),
        ('Additional Info', {
            'fields': ('remarks', 'added_by'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    date_hierarchy = 'created_at'
    
    def get_student_name(self, obj):
        return f"{obj.student.user.get_full_name()} ({obj.student.admission_number})"
    get_student_name.short_description = 'Student'
    get_student_name.admin_order_field = 'student__user__first_name'
    
    def marks_display(self, obj):
        return f"{obj.marks_obtained} / {obj.total_marks}"
    marks_display.short_description = 'Marks'
    
    def percentage_display(self, obj):
        percentage = obj.get_percentage()
        return f"{percentage:.2f}%" if percentage != 0 else "N/A"
    percentage_display.short_description = 'Percentage'
    
    def added_by_short(self, obj):
        return obj.added_by.user.get_full_name() if obj.added_by else "System"
    added_by_short.short_description = 'Added By'


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    """Enhanced Attendance admin with advanced filtering"""
    list_display = ['get_student_name', 'date', 'status_badge', 'marked_by_short', 'remarks_short']
    list_filter = ['status', 'date', 'marked_by']
    search_fields = ['student__user__first_name', 'student__user__last_name', 'student__admission_number']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Attendance Information', {
            'fields': ('student', 'date', 'status')
        }),
        ('Additional Info', {
            'fields': ('remarks', 'marked_by'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    date_hierarchy = 'date'
    ordering = ['-date']
    
    def get_student_name(self, obj):
        return f"{obj.student.user.get_full_name()} ({obj.student.admission_number})"
    get_student_name.short_description = 'Student'
    get_student_name.admin_order_field = 'student__user__first_name'
    
    def status_badge(self, obj):
        """Display status with color coding"""
        colors = {
            'present': 'green',
            'absent': 'red',
            'late': 'orange',
            'excused': 'blue'
        }
        color = colors.get(obj.status, 'gray')
        return f"<span style='color: {color}; font-weight: bold;'>⬤ {obj.status.upper()}</span>"
    status_badge.short_description = 'Status'
    status_badge.allow_tags = True
    
    def marked_by_short(self, obj):
        return obj.marked_by.user.get_full_name() if obj.marked_by else "System"
    marked_by_short.short_description = 'Marked By'
    
    def remarks_short(self, obj):
        remarks = obj.remarks or ""
        return remarks[:50] + "..." if len(remarks) > 50 else remarks
    remarks_short.short_description = 'Remarks'
