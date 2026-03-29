from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User

# User Profile to extend Django's User model
class UserProfile(models.Model):
    USER_TYPE_CHOICES = (
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
        ('parent', 'Parent'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.user_type}"


# Student Model
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    admission_number = models.CharField(max_length=20, unique=True)
    date_of_birth = models.DateField()
    grade = models.CharField(max_length=10)
    parent = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                               related_name='children', limit_choices_to={'profile__user_type': 'parent'})
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.admission_number}"


# Teacher Model
class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile')
    employee_id = models.CharField(max_length=20, unique=True)
    specialization = models.CharField(max_length=100)
    date_joined = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.employee_id}"


# Subject Model
class Subject(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True, null=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, related_name='subjects')
    
    def __str__(self):
        return f"{self.name} ({self.code})"


# Mark/Grade Model
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
    
    class Meta:
        unique_together = ['student', 'subject', 'term', 'year']
        ordering = ['-year', '-term', 'subject']
    
    def save(self, *args, **kwargs):
        # Auto-calculate grade based on percentage
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
    
    def get_percentage(self):
        if self.total_marks > 0:
            return (self.marks_obtained / self.total_marks) * 100
        return 0
    
    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.subject.name} - Term {self.term}/{self.year}"


# Attendance Model
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
    
    class Meta:
        unique_together = ['student', 'date']
        ordering = ['-date', 'student']
        verbose_name_plural = 'Attendance'
    
    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.date} - {self.status}"
