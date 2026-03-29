from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import UserProfile, Student, Teacher, Mark, Attendance, Subject


class LoginForm(forms.Form):
    """Form for user login"""
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your username',
            'autocomplete': 'off'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password',
            'autocomplete': 'current-password'
        })
    )


class BaseSignupForm(forms.Form):
    """Base form for user signup with common fields"""
    first_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First Name'
        })
    )
    last_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last Name'
        })
    )
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username'
        }),
        help_text='150 characters or fewer. Letters, digits and @/./+/-/_ only.'
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email Address'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password',
            'autocomplete': 'new-password'
        }),
        help_text='Password must be at least 8 characters long.'
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm Password',
            'autocomplete': 'new-password'
        })
    )
    phone = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Phone Number (optional)',
            'type': 'tel'
        })
    )

    def clean_username(self):
        """Validate username is unique"""
        username = self.cleaned_data.get('username', '').strip()
        if User.objects.filter(username=username).exists():
            raise ValidationError('Username already exists. Please choose a different username.')
        return username

    def clean_email(self):
        """Validate email is unique"""
        email = self.cleaned_data.get('email', '').strip()
        if User.objects.filter(email=email).exists():
            raise ValidationError('Email already registered. Please use a different email.')
        return email

    def clean_password(self):
        """Validate password strength"""
        password = self.cleaned_data.get('password', '')
        if len(password) < 8:
            raise ValidationError('Password must be at least 8 characters long.')
        if not any(char.isupper() for char in password):
            raise ValidationError('Password must contain at least one uppercase letter.')
        if not any(char.isdigit() for char in password):
            raise ValidationError('Password must contain at least one digit.')
        return password

    def clean(self):
        """Validate passwords match"""
        cleaned_data = super().clean() or {}
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password:
            if password != confirm_password:
                raise ValidationError('Passwords do not match.')
        return cleaned_data


class StudentSignupForm(forms.Form):
    """Form for student registration - minimal form with just name, password, admission_number, and grade"""
    first_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First Name'
        })
    )
    last_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last Name'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password',
            'autocomplete': 'new-password'
        }),
        help_text='Password must be at least 8 characters long.'
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm Password',
            'autocomplete': 'new-password'
        })
    )
    admission_number = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Admission Number'
        })
    )
    grade = forms.CharField(
        max_length=10,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Grade/Class (e.g., 10A, 9B)'
        })
    )

    def clean_admission_number(self):
        """Validate admission number is unique and can be used as username"""
        admission_number = self.cleaned_data.get('admission_number', '').strip()
        if Student.objects.filter(admission_number=admission_number).exists():
            raise ValidationError('Admission number already exists. Please use a different one.')
        # Check if admission_number would conflict with existing usernames
        if User.objects.filter(username=admission_number).exists():
            raise ValidationError('This admission number is already in use.')
        return admission_number

    def clean_password(self):
        """Validate password strength"""
        password = self.cleaned_data.get('password', '')
        if len(password) < 8:
            raise ValidationError('Password must be at least 8 characters long.')
        if not any(char.isupper() for char in password):
            raise ValidationError('Password must contain at least one uppercase letter.')
        if not any(char.isdigit() for char in password):
            raise ValidationError('Password must contain at least one digit.')
        return password

    def clean(self):
        """Validate passwords match"""
        cleaned_data = super().clean() or {}
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password:
            if password != confirm_password:
                raise ValidationError('Passwords do not match.')
        return cleaned_data


class TeacherSignupForm(forms.Form):
    """Form for teacher registration - minimal form with just name, password, and employee_id"""
    first_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First Name'
        })
    )
    last_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last Name'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password',
            'autocomplete': 'new-password'
        }),
        help_text='Password must be at least 8 characters long.'
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm Password',
            'autocomplete': 'new-password'
        })
    )
    employee_id = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Employee ID'
        })
    )

    def clean_employee_id(self):
        """Validate employee ID is unique"""
        employee_id = self.cleaned_data.get('employee_id', '').strip()
        if Teacher.objects.filter(employee_id=employee_id).exists():
            raise ValidationError('Employee ID already exists. Please use a different one.')
        return employee_id

    def clean_password(self):
        """Validate password strength"""
        password = self.cleaned_data.get('password', '')
        if len(password) < 8:
            raise ValidationError('Password must be at least 8 characters long.')
        if not any(char.isupper() for char in password):
            raise ValidationError('Password must contain at least one uppercase letter.')
        if not any(char.isdigit() for char in password):
            raise ValidationError('Password must contain at least one digit.')
        return password

    def clean(self):
        """Validate passwords match"""
        cleaned_data = super().clean() or {}
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password:
            if password != confirm_password:
                raise ValidationError('Passwords do not match.')
        return cleaned_data


class ParentSignupForm(BaseSignupForm):
    """Form for parent registration"""
    address = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Address (optional)',
            'rows': 3
        })
    )


class MarkForm(forms.ModelForm):
    """Form for adding/editing marks"""
    class Meta:
        model = Mark
        fields = ['student', 'subject', 'term', 'year', 'marks_obtained', 'total_marks', 'remarks']
        widgets = {
            'student': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'subject': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'term': forms.Select(attrs={
                'class': 'form-control'
            }),
            'year': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 2000,
                'max': 2100,
                'placeholder': 'Year'
            }),
            'marks_obtained': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Marks Obtained'
            }),
            'total_marks': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'value': '100',
                'placeholder': 'Total Marks'
            }),
            'remarks': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Remarks (optional)'
            })
        }

    def clean(self):
        """Validate marks data"""
        cleaned_data = super().clean() or {}
        marks_obtained = cleaned_data.get('marks_obtained')
        total_marks = cleaned_data.get('total_marks')

        if marks_obtained is not None and total_marks is not None:
            if marks_obtained < 0:
                raise ValidationError('Marks obtained cannot be negative.')
            if total_marks <= 0:
                raise ValidationError('Total marks must be greater than 0.')
            if marks_obtained > total_marks:
                raise ValidationError('Marks obtained cannot be greater than total marks.')
        
        return cleaned_data


class AttendanceForm(forms.ModelForm):
    """Form for marking attendance"""
    class Meta:
        model = Attendance
        fields = ['status', 'remarks']
        widgets = {
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
            'remarks': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Add remarks if needed'
            })
        }


class BulkAttendanceForm(forms.Form):
    """Form for marking attendance for multiple students at once"""
    attendance_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'required': True
        })
    )
    
    def get_attendance_formset(self, students):
        """Generate a formset for marking attendance for multiple students"""
        AttendanceFormSet = forms.modelformset_factory(
            Attendance,
            form=AttendanceForm,
            extra=0
        )
        return AttendanceFormSet(queryset=Attendance.objects.none())


class FilterAttendanceForm(forms.Form):
    """Form for filtering attendance records"""
    MONTH_CHOICES = [
        ('', 'All Months'),
        ('01', 'January'),
        ('02', 'February'),
        ('03', 'March'),
        ('04', 'April'),
        ('05', 'May'),
        ('06', 'June'),
        ('07', 'July'),
        ('08', 'August'),
        ('09', 'September'),
        ('10', 'October'),
        ('11', 'November'),
        ('12', 'December'),
    ]

    student = forms.ModelChoiceField(
        queryset=Student.objects.select_related('user').all(),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='Student'
    )
    status = forms.ChoiceField(
        choices=[('', 'All Status')] + list(Attendance.STATUS_CHOICES),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'placeholder': 'From Date'
        })
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'placeholder': 'To Date'
        })
    )

    def clean(self):
        """Validate date range"""
        cleaned_data = super().clean() or {}
        date_from = cleaned_data.get('date_from')
        date_to = cleaned_data.get('date_to')

        if date_from and date_to and date_from > date_to:
            raise ValidationError('Start date cannot be after end date.')
        
        return cleaned_data


class FilterMarkForm(forms.Form):
    """Form for filtering marks"""
    student = forms.ModelChoiceField(
        queryset=Student.objects.select_related('user').all(),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='Student'
    )
    subject = forms.ModelChoiceField(
        queryset=Subject.objects.all(),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='Subject'
    )
    term = forms.ChoiceField(
        choices=[('', 'All Terms')] + list(Mark.TERM_CHOICES),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    year = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': 2000,
            'max': 2100,
            'placeholder': 'Year'
        })
    )
