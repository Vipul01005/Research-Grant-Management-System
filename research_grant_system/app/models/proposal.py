"""
Proposal & Document Models - Phase 5
Handles research proposal submissions and document management.
"""
from datetime import datetime
from app.extensions import db


class Proposal(db.Model):
    """
    Research Proposal model.
    
    Status Flow:
        draft -> submitted -> under_review -> reviewed -> approved/rejected -> funded
    """
    __tablename__ = 'proposals'
    
    # Status choices
    STATUS_DRAFT = 'draft'
    STATUS_SUBMITTED = 'submitted'
    STATUS_UNDER_REVIEW = 'under_review'
    STATUS_REVIEWED = 'reviewed'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'
    STATUS_FUNDED = 'funded'
    
    STATUS_CHOICES = [
        (STATUS_DRAFT, 'Draft'),
        (STATUS_SUBMITTED, 'Submitted'),
        (STATUS_UNDER_REVIEW, 'Under Review'),
        (STATUS_REVIEWED, 'Reviewed'),
        (STATUS_APPROVED, 'Approved'),
        (STATUS_REJECTED, 'Rejected'),
        (STATUS_FUNDED, 'Funded')
    ]
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Proposal content
    title = db.Column(db.String(255), nullable=False)
    abstract = db.Column(db.Text, nullable=False)
    objectives = db.Column(db.Text)
    methodology = db.Column(db.Text)
    expected_outcomes = db.Column(db.Text)
    
    # Budget and timeline
    requested_amount = db.Column(db.Float, nullable=False)
    duration_months = db.Column(db.Integer, default=12)
    
    # Status tracking
    status = db.Column(db.String(50), default=STATUS_DRAFT, index=True)
    
    # Foreign keys
    researcher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Dates
    submission_date = db.Column(db.DateTime)
    deadline = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    documents = db.relationship('ProposalDocument', backref='proposal', 
                               lazy='dynamic', cascade='all, delete-orphan')
    reviews = db.relationship('Review', backref='proposal', 
                             lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Proposal {self.id}: {self.title[:50]}>'
    
    def submit(self):
        """Submit the proposal for review."""
        if self.status == self.STATUS_DRAFT:
            self.status = self.STATUS_SUBMITTED
            self.submission_date = datetime.utcnow()
            db.session.commit()
            return True
        return False
    
    def start_review(self):
        """Mark proposal as under review."""
        if self.status == self.STATUS_SUBMITTED:
            self.status = self.STATUS_UNDER_REVIEW
            db.session.commit()
            return True
        return False
    
    def mark_reviewed(self):
        """Mark proposal as reviewed by all reviewers."""
        if self.status == self.STATUS_UNDER_REVIEW:
            self.status = self.STATUS_REVIEWED
            db.session.commit()
            return True
        return False
    
    def approve(self):
        """Approve the proposal."""
        if self.status in [self.STATUS_REVIEWED, self.STATUS_UNDER_REVIEW]:
            self.status = self.STATUS_APPROVED
            db.session.commit()
            return True
        return False
    
    def reject(self):
        """Reject the proposal."""
        if self.status in [self.STATUS_REVIEWED, self.STATUS_UNDER_REVIEW]:
            self.status = self.STATUS_REJECTED
            db.session.commit()
            return True
        return False
    
    def fund(self):
        """Mark proposal as funded."""
        if self.status == self.STATUS_APPROVED:
            self.status = self.STATUS_FUNDED
            db.session.commit()
            return True
        return False
    
    def can_edit(self):
        """Check if proposal can be edited."""
        return self.status == self.STATUS_DRAFT
    
    def can_submit(self):
        """Check if proposal can be submitted."""
        return self.status == self.STATUS_DRAFT and self.title and self.abstract
    
    def get_average_score(self):
        """Calculate average score from all reviews."""
        completed_reviews = [r for r in self.reviews if r.status == 'completed' and r.score]
        if not completed_reviews:
            return None
        total = sum(r.score for r in completed_reviews)
        return round(total / len(completed_reviews), 1)
    
    def get_review_count(self):
        """Get count of completed reviews."""
        return self.reviews.filter_by(status='completed').count()
    
    @staticmethod
    def get_status_choices():
        """Return status choices for forms/filters."""
        return Proposal.STATUS_CHOICES
    
    @classmethod
    def get_by_researcher(cls, researcher_id):
        """Get all proposals by a specific researcher."""
        return cls.query.filter_by(researcher_id=researcher_id).order_by(cls.created_at.desc()).all()
    
    @classmethod
    def get_pending_review(cls):
        """Get all proposals pending review assignment."""
        return cls.query.filter_by(status=cls.STATUS_SUBMITTED).order_by(cls.submission_date.asc()).all()
    
    @classmethod
    def get_under_review(cls):
        """Get all proposals currently under review."""
        return cls.query.filter_by(status=cls.STATUS_UNDER_REVIEW).all()


class ProposalDocument(db.Model):
    """
    Document attached to a proposal.
    Supports version control for document updates.
    """
    __tablename__ = 'proposal_documents'
    
    # Document types
    TYPE_PROPOSAL = 'proposal'
    TYPE_BUDGET = 'budget'
    TYPE_CV = 'cv'
    TYPE_SUPPORTING = 'supporting'
    TYPE_OTHER = 'other'
    
    DOCUMENT_TYPES = [
        (TYPE_PROPOSAL, 'Proposal Document'),
        (TYPE_BUDGET, 'Budget Breakdown'),
        (TYPE_CV, 'Curriculum Vitae'),
        (TYPE_SUPPORTING, 'Supporting Document'),
        (TYPE_OTHER, 'Other')
    ]
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign key
    proposal_id = db.Column(db.Integer, db.ForeignKey('proposals.id'), nullable=False)
    
    # File information
    filename = db.Column(db.String(255), nullable=False)  # Stored filename (UUID)
    original_filename = db.Column(db.String(255), nullable=False)  # Original upload name
    file_type = db.Column(db.String(50), default=TYPE_OTHER)
    file_extension = db.Column(db.String(10))
    file_size = db.Column(db.Integer)  # Size in bytes
    
    # Version control
    version = db.Column(db.Integer, default=1)
    is_current = db.Column(db.Boolean, default=True)
    
    # Timestamps
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Document {self.original_filename} v{self.version}>'
    
    def get_file_size_formatted(self):
        """Return file size in human-readable format."""
        if not self.file_size:
            return "Unknown"
        
        for unit in ['B', 'KB', 'MB', 'GB']:
            if self.file_size < 1024:
                return f"{self.file_size:.1f} {unit}"
            self.file_size /= 1024
        return f"{self.file_size:.1f} TB"
    
    @staticmethod
    def get_type_choices():
        """Return document type choices for forms."""
        return ProposalDocument.DOCUMENT_TYPES
