"""
User Model - Phase 4
Handles user authentication and role-based access.
"""
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app.extensions import db, login_manager


class User(db.Model, UserMixin):
    """
    User model with role-based access control.
    
    Roles:
        - researcher: Can submit and track proposals
        - reviewer: Can review and score assigned proposals
        - hod: Head of Department - Can approve/reject proposals
        - admin: Can manage users, assign reviewers, allocate grants
    """
    __tablename__ = 'users'
    
    # Role choices
    ROLE_RESEARCHER = 'researcher'
    ROLE_REVIEWER = 'reviewer'
    ROLE_HOD = 'hod'
    ROLE_ADMIN = 'admin'
    
    ROLES = [
        (ROLE_RESEARCHER, 'Researcher'),
        (ROLE_REVIEWER, 'Reviewer'),
        (ROLE_HOD, 'Head of Department'),
        (ROLE_ADMIN, 'Administrator')
    ]
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Authentication fields
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    
    # Profile fields
    full_name = db.Column(db.String(150), nullable=False)
    department = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    
    # Role and status
    role = db.Column(db.String(20), nullable=False, default=ROLE_RESEARCHER)
    is_active = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    proposals = db.relationship('Proposal', backref='researcher', lazy='dynamic',
                               foreign_keys='Proposal.researcher_id')
    reviews = db.relationship('Review', backref='reviewer', lazy='dynamic',
                             foreign_keys='Review.reviewer_id')
    
    def __repr__(self):
        return f'<User {self.username} ({self.role})>'
    
    def set_password(self, password):
        """Hash and set the user's password."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if the provided password matches the hash."""
        return check_password_hash(self.password_hash, password)
    
    def update_last_login(self):
        """Update the last login timestamp."""
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    # Role checking methods
    def is_researcher(self):
        return self.role == self.ROLE_RESEARCHER
    
    def is_reviewer(self):
        return self.role == self.ROLE_REVIEWER
    
    def is_hod(self):
        return self.role == self.ROLE_HOD
    
    def is_admin(self):
        return self.role == self.ROLE_ADMIN
    
    def can_submit_proposals(self):
        """Check if user can submit proposals."""
        return self.role == self.ROLE_RESEARCHER
    
    def can_review_proposals(self):
        """Check if user can review proposals."""
        return self.role in [self.ROLE_REVIEWER, self.ROLE_HOD]
    
    def can_approve_proposals(self):
        """Check if user can approve/reject proposals."""
        return self.role in [self.ROLE_HOD, self.ROLE_ADMIN]
    
    def can_manage_users(self):
        """Check if user can manage other users."""
        return self.role == self.ROLE_ADMIN
    
    def can_assign_reviewers(self):
        """Check if user can assign reviewers to proposals."""
        return self.role in [self.ROLE_HOD, self.ROLE_ADMIN]
    
    def can_allocate_grants(self):
        """Check if user can allocate grants."""
        return self.role == self.ROLE_ADMIN
    
    @staticmethod
    def get_role_choices():
        """Return role choices for forms."""
        return User.ROLES
    
    @classmethod
    def get_by_email(cls, email):
        """Get user by email address."""
        return cls.query.filter_by(email=email.lower()).first()
    
    @classmethod
    def get_by_username(cls, username):
        """Get user by username."""
        return cls.query.filter_by(username=username).first()
    
    @classmethod
    def get_users_by_role(cls, role):
        """Get all users with a specific role."""
        return cls.query.filter_by(role=role, is_active=True).all()
    
    @classmethod
    def get_all_reviewers(cls):
        """Get all active reviewers."""
        return cls.get_users_by_role(cls.ROLE_REVIEWER)
    
    @classmethod
    def get_all_researchers(cls):
        """Get all active researchers."""
        return cls.get_users_by_role(cls.ROLE_RESEARCHER)


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login."""
    return User.query.get(int(user_id))
