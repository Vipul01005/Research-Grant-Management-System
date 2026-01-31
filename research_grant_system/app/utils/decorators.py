"""
Utility decorators for role-based access control.
"""
from functools import wraps
from flask import abort, flash, redirect, url_for
from flask_login import current_user


def role_required(*roles):
    """
    Decorator to restrict access to specific user roles.
    
    Usage:
        @app.route('/admin/users')
        @login_required
        @role_required('admin')
        def admin_users():
            ...
        
        @app.route('/review/assign')
        @login_required
        @role_required('admin', 'hod')
        def assign_reviewer():
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('auth.login'))
            
            if current_user.role not in roles:
                flash('You do not have permission to access this page.', 'danger')
                abort(403)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def researcher_required(f):
    """Decorator to restrict access to researchers only."""
    return role_required('researcher')(f)


def reviewer_required(f):
    """Decorator to restrict access to reviewers only."""
    return role_required('reviewer')(f)


def hod_required(f):
    """Decorator to restrict access to HOD only."""
    return role_required('hod')(f)


def admin_required(f):
    """Decorator to restrict access to admins only."""
    return role_required('admin')(f)
