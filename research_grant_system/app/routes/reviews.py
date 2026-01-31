"""
Review Routes - Phase 6
Handles review assignment, evaluation, and scoring.
"""
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models.review import Review
from app.models.proposal import Proposal
from app.models.user import User
from app.forms.review_forms import ReviewForm, QuickReviewForm, AssignReviewerForm, ReviewFilterForm
from app.utils.decorators import role_required

reviews_bp = Blueprint('reviews', __name__)


@reviews_bp.route('/')
@login_required
@role_required('reviewer', 'hod', 'admin')
def list_reviews():
    """List reviews based on user role."""
    form = ReviewFilterForm(request.args)
    
    if current_user.is_reviewer():
        query = Review.query.filter_by(reviewer_id=current_user.id)
    else:
        # HOD and Admin see all reviews
        query = Review.query
    
    # Apply filters
    if form.status.data:
        query = query.filter_by(status=form.status.data)
    
    reviews = query.order_by(Review.assigned_date.desc()).all()
    
    return render_template('reviews/list.html', reviews=reviews, form=form)


@reviews_bp.route('/assigned')
@login_required
@role_required('reviewer')
def assigned_reviews():
    """View proposals assigned to the current reviewer."""
    pending = Review.query.filter_by(
        reviewer_id=current_user.id,
        status=Review.STATUS_PENDING
    ).order_by(Review.deadline.asc()).all()
    
    in_progress = Review.query.filter_by(
        reviewer_id=current_user.id,
        status=Review.STATUS_IN_PROGRESS
    ).order_by(Review.deadline.asc()).all()
    
    completed = Review.query.filter_by(
        reviewer_id=current_user.id,
        status=Review.STATUS_COMPLETED
    ).order_by(Review.completed_date.desc()).limit(10).all()
    
    return render_template('reviews/assigned.html', 
                          pending=pending, 
                          in_progress=in_progress,
                          completed=completed)


@reviews_bp.route('/<int:review_id>')
@login_required
def view_review(review_id):
    """View a specific review."""
    review = Review.query.get_or_404(review_id)
    
    # Check access
    if current_user.is_reviewer() and review.reviewer_id != current_user.id:
        flash('You do not have permission to view this review.', 'danger')
        return redirect(url_for('reviews.assigned_reviews'))
    
    proposal = Proposal.query.get(review.proposal_id)
    
    return render_template('reviews/view.html', review=review, proposal=proposal)


@reviews_bp.route('/<int:review_id>/start', methods=['POST'])
@login_required
@role_required('reviewer')
def start_review(review_id):
    """Start working on a review."""
    review = Review.query.get_or_404(review_id)
    
    # Check ownership
    if review.reviewer_id != current_user.id:
        flash('You do not have permission to modify this review.', 'danger')
        return redirect(url_for('reviews.assigned_reviews'))
    
    if review.start_review():
        flash('Review started. You can now evaluate the proposal.', 'success')
    else:
        flash('Could not start review.', 'warning')
    
    return redirect(url_for('reviews.evaluate', review_id=review_id))


@reviews_bp.route('/<int:review_id>/evaluate', methods=['GET', 'POST'])
@login_required
@role_required('reviewer')
def evaluate(review_id):
    """Evaluate and score a proposal."""
    review = Review.query.get_or_404(review_id)
    
    # Check ownership
    if review.reviewer_id != current_user.id:
        flash('You do not have permission to evaluate this proposal.', 'danger')
        return redirect(url_for('reviews.assigned_reviews'))
    
    # Check if already completed
    if review.status == Review.STATUS_COMPLETED:
        flash('This review has already been completed.', 'info')
        return redirect(url_for('reviews.view_review', review_id=review_id))
    
    # Auto-start if pending
    if review.status == Review.STATUS_PENDING:
        review.start_review()
    
    proposal = Proposal.query.get(review.proposal_id)
    form = ReviewForm(obj=review)
    
    if form.validate_on_submit():
        # Update review with form data
        review.technical_merit = form.technical_merit.data
        review.feasibility = form.feasibility.data
        review.impact = form.impact.data
        review.budget_appropriateness = form.budget_appropriateness.data
        review.score = form.score.data
        review.strengths = form.strengths.data
        review.weaknesses = form.weaknesses.data
        review.comments = form.comments.data
        review.suggestions = form.suggestions.data
        review.recommendation = form.recommendation.data
        
        if 'save_draft' in request.form:
            # Save as draft
            db.session.commit()
            flash('Review saved as draft.', 'info')
            return redirect(url_for('reviews.evaluate', review_id=review_id))
        else:
            # Submit the review
            review.status = Review.STATUS_COMPLETED
            review.completed_date = datetime.utcnow()
            
            # Check if all reviews for this proposal are complete
            all_reviews = Review.query.filter_by(proposal_id=review.proposal_id).all()
            if all(r.status == Review.STATUS_COMPLETED for r in all_reviews):
                proposal.mark_reviewed()
            
            db.session.commit()
            flash('Review submitted successfully!', 'success')
            return redirect(url_for('reviews.assigned_reviews'))
    
    # Get proposal documents for reference
    documents = proposal.documents.filter_by(is_current=True).all()
    
    return render_template('reviews/evaluate.html', 
                          form=form, 
                          review=review, 
                          proposal=proposal,
                          documents=documents)


@reviews_bp.route('/proposal/<int:proposal_id>/assign', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'hod')
def assign_reviewer(proposal_id):
    """Assign a reviewer to a proposal."""
    proposal = Proposal.query.get_or_404(proposal_id)
    
    # Check if proposal can be reviewed
    if proposal.status not in [Proposal.STATUS_SUBMITTED, Proposal.STATUS_UNDER_REVIEW]:
        flash('This proposal is not available for review assignment.', 'warning')
        return redirect(url_for('proposals.view', proposal_id=proposal_id))
    
    form = AssignReviewerForm()
    
    # Get available reviewers (exclude those already assigned)
    assigned_reviewer_ids = [r.reviewer_id for r in proposal.reviews]
    available_reviewers = User.query.filter(
        User.role == 'reviewer',
        User.is_active == True,
        ~User.id.in_(assigned_reviewer_ids) if assigned_reviewer_ids else True
    ).all()
    
    form.reviewer_id.choices = [(0, 'Select a reviewer...')] + [
        (r.id, f'{r.full_name} ({r.department or "No Department"})') 
        for r in available_reviewers
    ]
    
    if form.validate_on_submit():
        if form.reviewer_id.data == 0:
            flash('Please select a reviewer.', 'warning')
        else:
            review = Review.assign_reviewer(
                proposal_id=proposal_id,
                reviewer_id=form.reviewer_id.data,
                assigned_by_id=current_user.id,
                deadline=form.deadline.data
            )
            
            if review:
                flash('Reviewer assigned successfully!', 'success')
                return redirect(url_for('proposals.view', proposal_id=proposal_id))
            else:
                flash('This reviewer is already assigned to this proposal.', 'warning')
    
    # Get current assignments
    current_reviews = proposal.reviews.all()
    
    return render_template('reviews/assign.html', 
                          form=form, 
                          proposal=proposal,
                          current_reviews=current_reviews,
                          available_reviewers=available_reviewers)


@reviews_bp.route('/<int:review_id>/remove', methods=['POST'])
@login_required
@role_required('admin', 'hod')
def remove_assignment(review_id):
    """Remove a reviewer assignment."""
    review = Review.query.get_or_404(review_id)
    proposal_id = review.proposal_id
    
    # Can only remove pending reviews
    if review.status != Review.STATUS_PENDING:
        flash('Cannot remove a review that has already been started.', 'warning')
        return redirect(url_for('reviews.assign_reviewer', proposal_id=proposal_id))
    
    db.session.delete(review)
    db.session.commit()
    
    flash('Reviewer assignment removed.', 'success')
    return redirect(url_for('reviews.assign_reviewer', proposal_id=proposal_id))


@reviews_bp.route('/proposal/<int:proposal_id>/summary')
@login_required
@role_required('admin', 'hod')
def review_summary(proposal_id):
    """View summary of all reviews for a proposal."""
    proposal = Proposal.query.get_or_404(proposal_id)
    reviews = proposal.reviews.all()
    
    # Calculate statistics
    completed_reviews = [r for r in reviews if r.status == Review.STATUS_COMPLETED]
    
    stats = {
        'total_reviews': len(reviews),
        'completed': len(completed_reviews),
        'pending': len([r for r in reviews if r.status == Review.STATUS_PENDING]),
        'in_progress': len([r for r in reviews if r.status == Review.STATUS_IN_PROGRESS])
    }
    
    if completed_reviews:
        stats['average_score'] = round(
            sum(r.score for r in completed_reviews if r.score) / len(completed_reviews), 1
        )
        
        # Count recommendations
        stats['approve_count'] = len([r for r in completed_reviews if r.recommendation == 'approve'])
        stats['reject_count'] = len([r for r in completed_reviews if r.recommendation == 'reject'])
        stats['revise_count'] = len([r for r in completed_reviews if r.recommendation == 'revise'])
    else:
        stats['average_score'] = None
        stats['approve_count'] = 0
        stats['reject_count'] = 0
        stats['revise_count'] = 0
    
    return render_template('reviews/summary.html', 
                          proposal=proposal, 
                          reviews=reviews,
                          stats=stats)
