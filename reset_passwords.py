"""
Reset passwords for all test users
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from django.contrib.auth.models import User

# Reset passwords
users_passwords = {
    'admin': 'admin123',
    'teacher1': 'teacher123',
    'teacher2': 'teacher123',
    'parent1': 'parent123',
    'parent2': 'parent123',
    'student1': 'student123',
    'student2': 'student123',
    'student3': 'student123',
}

print("Resetting passwords...")
for username, password in users_passwords.items():
    try:
        user = User.objects.get(username=username)
        user.set_password(password)
        user.save()
        print(f"[OK] Password reset for {username}: {password}")
    except User.DoesNotExist:
        print(f"[ERROR] User {username} not found")

print("\nPassword reset complete!")
print("\nLogin credentials:")
print("=" * 50)
print("Admin:   username: admin    password: admin123")
print("Teacher: username: teacher1 password: teacher123")
print("Student: username: student1 password: student123")
print("Parent:  username: parent1  password: parent123")
print("=" * 50)
