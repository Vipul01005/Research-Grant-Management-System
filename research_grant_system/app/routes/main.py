"""
Main routes - Home page and general routes.
"""
from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user, login_required

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Home page - redirects based on user role."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('index.html')


@main_bp.route('/dashboard')
@login_required
def dashboard():
    """
    Main dashboard - redirects to role-specific dashboard.
    """
    role = current_user.role
    
    if role == 'admin':
        return redirect(url_for('main.admin_dashboard'))
    elif role == 'hod':
        return redirect(url_for('main.hod_dashboard'))
    elif role == 'reviewer':
        return redirect(url_for('main.reviewer_dashboard'))
    else:  # researcher
        return redirect(url_for('main.researcher_dashboard'))


@main_bp.route('/dashboard/researcher')
@login_required
def researcher_dashboard():
    """Researcher dashboard."""
    from app.models.proposal import Proposal
    
    proposals = Proposal.query.filter_by(researcher_id=current_user.id).order_by(Proposal.created_at.desc()).all()
    
    # Statistics
    stats = {
        'total': len(proposals),
        'draft': len([p for p in proposals if p.status == 'draft']),
        'submitted': len([p for p in proposals if p.status == 'submitted']),
        'approved': len([p for p in proposals if p.status == 'approved']),
        'funded': len([p for p in proposals if p.status == 'funded'])
    }
    
    return render_template('researcher/dashboard.html', proposals=proposals, stats=stats)


@main_bp.route('/dashboard/reviewer')
@login_required
def reviewer_dashboard():
    """Reviewer dashboard."""
    from app.models.review import Review
    
    reviews = Review.query.filter_by(reviewer_id=current_user.id).order_by(Review.assigned_date.desc()).all()
    
    stats = {
        'total': len(reviews),
        'pending': len([r for r in reviews if r.status == 'pending']),
        'completed': len([r for r in reviews if r.status == 'completed'])
    }
    
    return render_template('reviewer/dashboard.html', reviews=reviews, stats=stats)


@main_bp.route('/dashboard/hod')
@login_required
def hod_dashboard():
    """Head of Department dashboard."""
    from app.models.proposal import Proposal
    
    # Get proposals that are under review or awaiting approval
    proposals = Proposal.query.filter(
        Proposal.status.in_(['under_review', 'reviewed'])
    ).order_by(Proposal.submission_date.desc()).all()
    
    return render_template('hod/dashboard.html', proposals=proposals)


@main_bp.route('/dashboard/admin')
@login_required
def admin_dashboard():
    """Admin dashboard."""
    from app.models.user import User
    from app.models.proposal import Proposal
    
    users = User.query.all()
    proposals = Proposal.query.order_by(Proposal.created_at.desc()).all()
    
    stats = {
        'total_users': len(users),
        'researchers': len([u for u in users if u.role == 'researcher']),
        'reviewers': len([u for u in users if u.role == 'reviewer']),
        'total_proposals': len(proposals),
        'pending_review': len([p for p in proposals if p.status == 'submitted'])
    }
    
    return render_template('admin/dashboard.html', users=users, proposals=proposals, stats=stats)
