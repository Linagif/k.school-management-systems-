"""
Setup script to create sample data for the School Management System
Run this script after creating a superuser: python manage.py shell < setup_data.py
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import UserProfile, Student, Teacher, Subject, Mark
from datetime import date

print("Creating sample data...")

# Create Admin User
try:
    admin_user = User.objects.create_user(
        username='admin',
        password='admin123',
        email='admin@school.com',
        first_name='Admin',
        last_name='User',
        is_staff=True,
        is_superuser=True
    )
    UserProfile.objects.create(user=admin_user, user_type='admin', phone='1234567890')
    print("[OK] Admin user created (username: admin, password: admin123)")
except:
    print("[SKIP] Admin user already exists")

# Create Teacher Users
teachers_data = [
    {'username': 'teacher1', 'first_name': 'John', 'last_name': 'Smith', 'email': 'john@school.com', 'emp_id': 'T001', 'spec': 'Mathematics'},
    {'username': 'teacher2', 'first_name': 'Sarah', 'last_name': 'Johnson', 'email': 'sarah@school.com', 'emp_id': 'T002', 'spec': 'Science'},
]

for t_data in teachers_data:
    try:
        teacher_user = User.objects.create_user(
            username=t_data['username'],
            password='teacher123',
            email=t_data['email'],
            first_name=t_data['first_name'],
            last_name=t_data['last_name']
        )
        UserProfile.objects.create(user=teacher_user, user_type='teacher', phone='1234567890')
        Teacher.objects.create(
            user=teacher_user,
            employee_id=t_data['emp_id'],
            specialization=t_data['spec']
        )
        print(f"[OK] Teacher {t_data['username']} created (password: teacher123)")
    except:
        print(f"[SKIP] Teacher {t_data['username']} already exists")

# Create Parent Users
parents_data = [
    {'username': 'parent1', 'first_name': 'Michael', 'last_name': 'Brown', 'email': 'michael@parent.com'},
    {'username': 'parent2', 'first_name': 'Emily', 'last_name': 'Davis', 'email': 'emily@parent.com'},
]

parent_users = []
for p_data in parents_data:
    try:
        parent_user = User.objects.create_user(
            username=p_data['username'],
            password='parent123',
            email=p_data['email'],
            first_name=p_data['first_name'],
            last_name=p_data['last_name']
        )
        UserProfile.objects.create(user=parent_user, user_type='parent', phone='1234567890')
        parent_users.append(parent_user)
        print(f"[OK] Parent {p_data['username']} created (password: parent123)")
    except:
        print(f"[SKIP] Parent {p_data['username']} already exists")
        parent_users.append(User.objects.get(username=p_data['username']))

# Create Student Users
students_data = [
    {'username': 'student1', 'first_name': 'Alice', 'last_name': 'Brown', 'email': 'alice@student.com', 'adm': 'S001', 'grade': 'Grade 10', 'dob': date(2010, 5, 15), 'parent_idx': 0},
    {'username': 'student2', 'first_name': 'Bob', 'last_name': 'Brown', 'email': 'bob@student.com', 'adm': 'S002', 'grade': 'Grade 9', 'dob': date(2011, 8, 20), 'parent_idx': 0},
    {'username': 'student3', 'first_name': 'Charlie', 'last_name': 'Davis', 'email': 'charlie@student.com', 'adm': 'S003', 'grade': 'Grade 10', 'dob': date(2010, 3, 10), 'parent_idx': 1},
]

student_objects = []
for s_data in students_data:
    try:
        student_user = User.objects.create_user(
            username=s_data['username'],
            password='student123',
            email=s_data['email'],
            first_name=s_data['first_name'],
            last_name=s_data['last_name']
        )
        UserProfile.objects.create(user=student_user, user_type='student', phone='1234567890')
        student = Student.objects.create(
            user=student_user,
            admission_number=s_data['adm'],
            date_of_birth=s_data['dob'],
            grade=s_data['grade'],
            parent=parent_users[s_data['parent_idx']] if parent_users else None
        )
        student_objects.append(student)
        print(f"[OK] Student {s_data['username']} created (password: student123)")
    except:
        print(f"[SKIP] Student {s_data['username']} already exists")
        student_objects.append(Student.objects.get(admission_number=s_data['adm']))

# Create Subjects
subjects_data = [
    {'name': 'Mathematics', 'code': 'MATH101'},
    {'name': 'Science', 'code': 'SCI101'},
    {'name': 'English', 'code': 'ENG101'},
    {'name': 'History', 'code': 'HIST101'},
]

subject_objects = []
for subj_data in subjects_data:
    try:
        teacher = Teacher.objects.first()
        subject = Subject.objects.create(
            name=subj_data['name'],
            code=subj_data['code'],
            description=f"{subj_data['name']} course",
            teacher=teacher
        )
        subject_objects.append(subject)
        print(f"[OK] Subject {subj_data['name']} created")
    except:
        print(f"[SKIP] Subject {subj_data['name']} already exists")
        subject_objects.append(Subject.objects.get(code=subj_data['code']))

# Create Sample Marks
print("\nCreating sample marks...")
teacher = Teacher.objects.first()
if teacher and student_objects and subject_objects:
    marks_data = [
        {'student_idx': 0, 'subject_idx': 0, 'marks': 85, 'term': '1', 'year': 2024},
        {'student_idx': 0, 'subject_idx': 1, 'marks': 78, 'term': '1', 'year': 2024},
        {'student_idx': 1, 'subject_idx': 0, 'marks': 92, 'term': '1', 'year': 2024},
        {'student_idx': 1, 'subject_idx': 1, 'marks': 88, 'term': '1', 'year': 2024},
        {'student_idx': 2, 'subject_idx': 0, 'marks': 75, 'term': '1', 'year': 2024},
        {'student_idx': 2, 'subject_idx': 1, 'marks': 82, 'term': '1', 'year': 2024},
    ]
    
    for mark_data in marks_data:
        try:
            Mark.objects.create(
                student=student_objects[mark_data['student_idx']],
                subject=subject_objects[mark_data['subject_idx']],
                term=mark_data['term'],
                year=mark_data['year'],
                marks_obtained=mark_data['marks'],
                total_marks=100,
                remarks='Good performance',
                added_by=teacher
            )
            print(f"[OK] Mark added for {student_objects[mark_data['student_idx']].user.first_name} in {subject_objects[mark_data['subject_idx']].name}")
        except:
            print(f"[SKIP] Mark already exists")

print("\n" + "="*50)
print("Setup complete! You can now login with:")
print("="*50)
print("Admin:   username: admin    password: admin123")
print("Teacher: username: teacher1 password: teacher123")
print("Student: username: student1 password: student123")
print("Parent:  username: parent1  password: parent123")
print("="*50)
