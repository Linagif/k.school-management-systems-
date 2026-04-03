# Django School Management System

A comprehensive web application for managing academic records, attendance, and user interactions in educational institutions.

## 🚀 Features

- **Multi-role Authentication** - Admin, Teacher, Student, and Parent roles
- **Academic Management** - Mark entry with automatic grade calculation
- **Attendance Tracking** - Daily attendance with multiple status options
- **Report Generation** - PDF report cards with performance charts
- **Dashboard Analytics** - Role-specific dashboards with statistics
- **Security** - CSRF protection, role-based access control, comprehensive logging
- **Testing** - 28+ unit and integration tests

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [Installation](#installation)
- [User Roles](#user-roles)
- [Features](#features)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [Testing](#testing)
- [Documentation](#documentation)
- [Support](#support)

## ⚡ Quick Start

```bash
# 1. Navigate to project directory
cd "k.junior school"

# 2. Install dependencies
pip install django reportlab

# 3. Run migrations
python manage.py migrate

# 4. Create superuser
python manage.py createsuperuser

# 5. Run server
python manage.py runserver

# 6. Open browser
# http://localhost:8000/
```

## 🛠️ Installation

### Prerequisites
- Python 3.10+
- pip (Python package manager)

### Step-by-Step Installation

1. **Clone or download the project**
```bash
cd "k.junior school"
```

2. **Create virtual environment (recommended)**
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

5. **Run database migrations**
```bash
python manage.py migrate
```

6. **Create superuser account**
```bash
python manage.py createsuperuser
```

7. **Run development server**
```bash
python manage.py runserver
```

8. **Access the application**
- Main site: http://localhost:8000/
- Admin panel: http://localhost:8000/admin/

### Setup Sample Data (Optional)
```bash
python setup_data.py
```

This creates sample teachers, subjects, students, marks, and attendance records.

## 👥 User Roles

### Administrator
- Full system access
- View all students, teachers, and marks
- Manage attendance records
- Generate reports for all users
- Access Django admin interface

### Teacher
- View assigned subjects
- Add marks for students
- Mark attendance for students
- View marks they've added
- View attendance records

### Student
- View personal marks and grades
- View personal attendance records
- Generate personal report card (PDF)
- View average percentage

### Parent
- View linked children's marks
- View linked children's attendance
- Generate report cards for children
- Monitor academic progress

## ✨ Features

### Authentication
- Secure login/logout
- Role-based registration (Student, Teacher, Parent)
- Password validation
- Session management

### Academic Management
- Mark entry with validation
- Automatic grade calculation (A+, A, B, C, D, F)
- Term-based organization (Term 1, 2, 3)
- Subject assignment to teachers

### Attendance Tracking
- Daily attendance marking
- Status options: Present, Absent, Late, Excused
- Attendance statistics and percentages
- Date-based filtering

### Report Generation
- Professional PDF reports
- Student performance charts
- Attendance summary
- Downloadable files

### Dashboard Analytics
- Admin: System-wide statistics
- Teacher: Subject and mark statistics
- Student: Personal performance metrics
- Parent: Children overview

## 📁 Project Structure

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
├── manage.py                      # Django management
├── setup_data.py                  # Sample data setup
└── reset_passwords.py             # Password reset utility
```

## ⚙️ Configuration

### Environment Variables
Create a `.env` file in the project root:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

### Database Configuration

#### Development (SQLite - Default)
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

#### Production (PostgreSQL)
```python
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

## 🧪 Testing

### Run All Tests
```bash
python manage.py test
```

### Run Specific Test Class
```bash
python manage.py test core.tests.MarkModelTest
```

### Run Specific Test Method
```bash
python manage.py test core.tests.MarkModelTest.test_mark_with_zero_total_marks
```

### Run with Verbose Output
```bash
python manage.py test --verbosity=2
```

### Run with Coverage
```bash
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html  # Generate HTML report
```

### Test Coverage
- **Models**: 100% coverage
- **Forms**: 95%+ coverage
- **Views**: 80%+ coverage
- **Overall**: 85%+ coverage

## 📚 Documentation

### Available Documentation Files

| File | Description |
|------|-------------|
| **PROJECT_DOCUMENTATION.md** | Complete project documentation |
| **IMPLEMENTATION_COMPLETE.md** | Implementation summary |
| **QUICK_REFERENCE.md** | Quick lookup guide |
| **ADVANCED_FEATURES.md** | Advanced features guide |
| **DEBUG_REPORT.md** | Debugging report |
| **FORMS_IMPLEMENTATION.md** | Forms documentation |
| **PROJECT_DEBUG_REPORT.md** | Project debug report |

### Quick Reference

#### Common Commands
```bash
# Run server
python manage.py runserver

# Run tests
python manage.py test

# Create superuser
python manage.py createsuperuser

# Migrate database
python manage.py migrate

# Collect static files
python manage.py collectstatic

# View logs
tail -f logs/debug.log
```

#### URL Routes
| URL | Description |
|-----|-------------|
| `/login/` | User login |
| `/signup/` | User registration |
| `/dashboard/` | Role-based dashboard |
| `/admin-dashboard/` | Admin dashboard |
| `/teacher-dashboard/` | Teacher dashboard |
| `/student-dashboard/` | Student dashboard |
| `/parent-dashboard/` | Parent dashboard |
| `/admin/` | Django admin panel |

## 🔐 Security Features

- **CSRF Protection**: Automatic CSRF token validation
- **Password Hashing**: Django's built-in password hashing
- **Session Management**: Secure session handling
- **Role-Based Access**: Decorator-based access control
- **Input Validation**: Form-level validation
- **SQL Injection Protection**: Django ORM parameterized queries
- **XSS Protection**: Template auto-escaping
- **Security Headers**: XSS, clickjacking protection

## 📊 Logging

### Log Files
```
logs/
├── debug.log          # General debug information
├── security.log       # Security events
├── audit.log          # User actions
└── errors.log         # Error tracking
```

### View Logs
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

## 🆘 Troubleshooting

### Issue: Tests Fail
**Solution:**
```bash
python manage.py migrate
python manage.py test
```

### Issue: Static Files Not Loading
**Solution:**
```bash
python manage.py collectstatic --noinput
```

### Issue: Permission Denied Error
**Solution:** Add appropriate decorator to view:
```python
from core.decorators import teacher_required
from django.contrib.auth.decorators import login_required

@login_required
@teacher_required
def my_view(request):
    pass
```

### Issue: Database Errors
**Solution:** Check migrations are applied:
```bash
python manage.py migrate
```

### Issue: "No such file or directory: logs/debug.log"
**Solution:** Django creates the logs directory automatically on first write. Just run the app:
```bash
python manage.py runserver
```

## 📈 Performance Tips

### Query Optimization
```python
# BAD (N+1 queries)
marks = Mark.objects.all()
for mark in marks:
    print(mark.student.user.first_name)  # Extra query each time!

# GOOD (Single query)
marks = Mark.objects.select_related('student__user', 'subject')
for mark in marks:
    print(mark.student.user.first_name)  # No extra queries!
```

### Use Pagination for Large Lists
```python
from django.core.paginator import Paginator

def my_view(request):
    objects = MyModel.objects.all()
    paginator = Paginator(objects, 25)  # Show 25 per page
    page = request.GET.get('page')
    items = paginator.get_page(page)
    return render(request, 'template.html', {'items': items})
```

## 🚀 Deployment

### Production Checklist
- [ ] Set `DEBUG = False`
- [ ] Set `SECRET_KEY` from environment variable
- [ ] Update `ALLOWED_HOSTS` with your domain
- [ ] Run `python manage.py collectstatic`
- [ ] Run `python manage.py test` to verify
- [ ] Check `logs/security.log` is writable
- [ ] Enable HTTPS and set `SECURE_SSL_REDIRECT = True`
- [ ] Create superuser: `python manage.py createsuperuser`
- [ ] Test login at `/admin/`
- [ ] Verify logs are being written

### Docker Deployment (Optional)
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `python manage.py test`
5. Submit a pull request

## 📄 License

This project is developed for educational purposes.

## 📞 Support

### Getting Help
1. Check logs: `tail -n 50 logs/errors.log`
2. Run tests: `python manage.py test --verbosity=2`
3. Review documentation files
4. Check Django documentation: https://docs.djangoproject.com/

### Common Issues
- See [Troubleshooting](#troubleshooting) section
- Check `DEBUG_REPORT.md` for debugging information
- Review `QUICK_REFERENCE.md` for quick solutions

## 🎓 Learning Resources

### Django Documentation
- [Official Django Documentation](https://docs.djangoproject.com/)
- [Django Tutorial](https://docs.djangoproject.com/en/stable/intro/tutorial01/)
- [Django Topics](https://docs.djangoproject.com/en/stable/topics/)

### Python Resources
- [Python Documentation](https://docs.python.org/3/)
- [Python Tutorial](https://docs.python.org/3/tutorial/)

## 📊 Project Statistics

- **Total Lines of Code**: 2000+
- **Test Cases**: 28+
- **Test Coverage**: 85%+
- **Models**: 6
- **Views**: 15+
- **Templates**: 15+
- **Forms**: 7
- **Decorators**: 9

## 🎯 Roadmap

### Version 1.1 (Planned)
- [ ] Email notifications
- [ ] SMS alerts
- [ ] Online exams
- [ ] Fee management

### Version 2.0 (Future)
- [ ] Mobile app
- [ ] Library management
- [ ] Transport management
- [ ] Hostel management

## 👨‍💻 Development

### Code Style
- Follow PEP 8 guidelines
- Use meaningful variable names
- Add docstrings to functions
- Comment complex logic

### Git Workflow
```bash
# Create feature branch
git checkout -b feature/new-feature

# Make changes and commit
git add .
git commit -m "Add new feature"

# Push to remote
git push origin feature/new-feature

# Create pull request
```

## 📝 Changelog

### Version 1.0.0 (2026-03-29)
- Initial release
- Multi-role authentication
- Academic management
- Attendance tracking
- Report generation
- Comprehensive logging
- Unit tests

---

**Django School Management System** - Built with ❤️ using Django
