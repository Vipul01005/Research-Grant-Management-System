"""
Review Model - Phase 6
Handles proposal reviews, scoring, and feedback.
"""
from datetime import datetime
from app.extensions import db


class Review(db.Model):
    """
    Review model for proposal evaluations.
    
    A review is assigned by Admin/HOD to a Reviewer for a specific proposal.
    The reviewer then scores and comments on the proposal.
    """
    __tablename__ = 'reviews'
    
    # Status choices
    STATUS_PENDING = 'pending'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_COMPLETED = 'completed'
    
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_IN_PROGRESS, 'In Progress'),
        (STATUS_COMPLETED, 'Completed')
    ]
    
    # Recommendation choices
    RECOMMEND_APPROVE = 'approve'
    RECOMMEND_REJECT = 'reject'
    RECOMMEND_REVISE = 'revise'
    
    RECOMMENDATION_CHOICES = [
        (RECOMMEND_APPROVE, 'Recommend Approval'),
        (RECOMMEND_REJECT, 'Recommend Rejection'),
        (RECOMMEND_REVISE, 'Requires Revision')
    ]
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign keys
    proposal_id = db.Column(db.Integer, db.ForeignKey('proposals.id'), nullable=False)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    assigned_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Scoring (1-10 scale)
    score = db.Column(db.Integer)  # Overall score
    technical_merit = db.Column(db.Integer)  # Technical quality score
    feasibility = db.Column(db.Integer)  # Feasibility score
    impact = db.Column(db.Integer)  # Potential impact score
    budget_appropriateness = db.Column(db.Integer)  # Budget justification score
    
    # Feedback
    comments = db.Column(db.Text)  # General comments
    strengths = db.Column(db.Text)  # Proposal strengths
    weaknesses = db.Column(db.Text)  # Proposal weaknesses
    suggestions = db.Column(db.Text)  # Suggestions for improvement
    
    # Recommendation
    recommendation = db.Column(db.String(50))  # approve, reject, revise
    
    # Status
    status = db.Column(db.String(50), default=STATUS_PENDING, index=True)
    
    # Timestamps
    assigned_date = db.Column(db.DateTime, default=datetime.utcnow)
    started_date = db.Column(db.DateTime)
    completed_date = db.Column(db.DateTime)
    deadline = db.Column(db.DateTime)
    
    # Relationship for assigned_by user
    assigned_by = db.relationship('User', foreign_keys=[assigned_by_id], backref='assigned_reviews')
    
    def __repr__(self):
        return f'<Review {self.id}: Proposal {self.proposal_id} by Reviewer {self.reviewer_id}>'
    
    def start_review(self):
        """Mark review as in progress."""
        if self.status == self.STATUS_PENDING:
            self.status = self.STATUS_IN_PROGRESS
            self.started_date = datetime.utcnow()
            db.session.commit()
            return True
        return False
    
    def complete_review(self, score, recommendation, comments=None):
        """Complete the review with score and recommendation."""
        self.score = score
        self.recommendation = recommendation
        if comments:
            self.comments = comments
        self.status = self.STATUS_COMPLETED
        self.completed_date = datetime.utcnow()
        
        # Update proposal status if needed
        self._check_all_reviews_complete()
        
        db.session.commit()
        return True
    
    def _check_all_reviews_complete(self):
        """Check if all reviews for this proposal are complete."""
        proposal = self.proposal
        all_reviews = Review.query.filter_by(proposal_id=self.proposal_id).all()
        
        if all(r.status == self.STATUS_COMPLETED for r in all_reviews):
            # All reviews complete, update proposal status
            proposal.mark_reviewed()
    
    def calculate_average_score(self):
        """Calculate average from all individual scores."""
        scores = [
            self.technical_merit,
            self.feasibility,
            self.impact,
            self.budget_appropriateness
        ]
        valid_scores = [s for s in scores if s is not None]
        
        if valid_scores:
            return round(sum(valid_scores) / len(valid_scores), 1)
        return self.score
    
    def is_overdue(self):
        """Check if the review is past its deadline."""
        if self.deadline and self.status != self.STATUS_COMPLETED:
            return datetime.utcnow() > self.deadline
        return False
    
    @staticmethod
    def get_status_choices():
        """Return status choices for forms/filters."""
        return Review.STATUS_CHOICES
    
    @staticmethod
    def get_recommendation_choices():
        """Return recommendation choices for forms."""
        return Review.RECOMMENDATION_CHOICES
    
    @classmethod
    def get_by_reviewer(cls, reviewer_id):
        """Get all reviews assigned to a specific reviewer."""
        return cls.query.filter_by(reviewer_id=reviewer_id).order_by(cls.assigned_date.desc()).all()
    
    @classmethod
    def get_pending_by_reviewer(cls, reviewer_id):
        """Get pending reviews for a specific reviewer."""
        return cls.query.filter_by(
            reviewer_id=reviewer_id,
            status=cls.STATUS_PENDING
        ).order_by(cls.deadline.asc()).all()
    
    @classmethod
    def get_by_proposal(cls, proposal_id):
        """Get all reviews for a specific proposal."""
        return cls.query.filter_by(proposal_id=proposal_id).all()
    
    @classmethod
    def assign_reviewer(cls, proposal_id, reviewer_id, assigned_by_id, deadline=None):
        """
        Assign a reviewer to a proposal.
        
        Returns:
            Review object if successful, None if already assigned
        """
        # Check if already assigned
        existing = cls.query.filter_by(
            proposal_id=proposal_id,
            reviewer_id=reviewer_id
        ).first()
        
        if existing:
            return None
        
        review = cls(
            proposal_id=proposal_id,
            reviewer_id=reviewer_id,
            assigned_by_id=assigned_by_id,
            deadline=deadline,
            status=cls.STATUS_PENDING
        )
        
        db.session.add(review)
        
        # Update proposal status if it's the first reviewer
        from app.models.proposal import Proposal
        proposal = Proposal.query.get(proposal_id)
        if proposal and proposal.status == Proposal.STATUS_SUBMITTED:
            proposal.start_review()
        
        db.session.commit()
        return review
