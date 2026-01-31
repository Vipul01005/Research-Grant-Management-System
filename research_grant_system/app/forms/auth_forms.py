"""
Authentication Forms - Phase 4
Forms for login, registration, and profile management.
"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, Regexp
from app.models.user import User


class LoginForm(FlaskForm):
    """User login form."""
    email = StringField('Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Please enter a valid email address')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required')
    ])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')


class RegistrationForm(FlaskForm):
    """User registration form."""
    email = StringField('Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Please enter a valid email address'),
        Length(max=120, message='Email must be less than 120 characters')
    ])
    username = StringField('Username', validators=[
        DataRequired(message='Username is required'),
        Length(min=3, max=80, message='Username must be between 3 and 80 characters'),
        Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
               'Username must start with a letter and contain only letters, numbers, dots, or underscores')
    ])
    full_name = StringField('Full Name', validators=[
        DataRequired(message='Full name is required'),
        Length(min=2, max=150, message='Full name must be between 2 and 150 characters')
    ])
    department = StringField('Department', validators=[
        Length(max=100, message='Department must be less than 100 characters')
    ])
    phone = StringField('Phone Number', validators=[
        Length(max=20, message='Phone number must be less than 20 characters')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required'),
        Length(min=6, message='Password must be at least 6 characters')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(message='Please confirm your password'),
        EqualTo('password', message='Passwords must match')
    ])
    role = SelectField('Role', choices=[
        ('researcher', 'Researcher'),
        ('reviewer', 'Reviewer')
    ], default='researcher')
    submit = SubmitField('Register')
    
    def validate_email(self, field):
        """Check if email is already registered."""
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError('This email is already registered.')
    
    def validate_username(self, field):
        """Check if username is already taken."""
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('This username is already taken.')


class ProfileForm(FlaskForm):
    """User profile edit form."""
    full_name = StringField('Full Name', validators=[
        DataRequired(message='Full name is required'),
        Length(min=2, max=150, message='Full name must be between 2 and 150 characters')
    ])
    department = StringField('Department', validators=[
        Length(max=100, message='Department must be less than 100 characters')
    ])
    phone = StringField('Phone Number', validators=[
        Length(max=20, message='Phone number must be less than 20 characters')
    ])
    submit = SubmitField('Update Profile')


class ChangePasswordForm(FlaskForm):
    """Change password form."""
    current_password = PasswordField('Current Password', validators=[
        DataRequired(message='Current password is required')
    ])
    new_password = PasswordField('New Password', validators=[
        DataRequired(message='New password is required'),
        Length(min=6, message='Password must be at least 6 characters')
    ])
    confirm_password = PasswordField('Confirm New Password', validators=[
        DataRequired(message='Please confirm your new password'),
        EqualTo('new_password', message='Passwords must match')
    ])
    submit = SubmitField('Change Password')


class AdminUserForm(FlaskForm):
    """Admin form for creating/editing users (includes all roles)."""
    email = StringField('Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Please enter a valid email address'),
        Length(max=120)
    ])
    username = StringField('Username', validators=[
        DataRequired(message='Username is required'),
        Length(min=3, max=80),
        Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
               'Username must start with a letter and contain only letters, numbers, dots, or underscores')
    ])
    full_name = StringField('Full Name', validators=[
        DataRequired(message='Full name is required'),
        Length(min=2, max=150)
    ])
    department = StringField('Department', validators=[
        Length(max=100)
    ])
    phone = StringField('Phone Number', validators=[
        Length(max=20)
    ])
    role = SelectField('Role', choices=[
        ('researcher', 'Researcher'),
        ('reviewer', 'Reviewer'),
        ('hod', 'Head of Department'),
        ('admin', 'Administrator')
    ])
    is_active = BooleanField('Active', default=True)
    password = PasswordField('Password (leave blank to keep current)', validators=[
        Length(min=6, message='Password must be at least 6 characters')
    ])
    submit = SubmitField('Save User')
