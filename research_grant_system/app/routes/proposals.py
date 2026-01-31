"""
Proposal Routes - Phase 5
Handles proposal submission, viewing, editing, and document management.
"""
import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, send_from_directory
from flask_login import login_required, current_user
from app.extensions import db
from app.models.proposal import Proposal, ProposalDocument
from app.forms.proposal_forms import ProposalForm, DocumentUploadForm, ProposalFilterForm
from app.utils.decorators import role_required
from app.utils.helpers import save_uploaded_file, delete_uploaded_file

proposals_bp = Blueprint('proposals', __name__)


@proposals_bp.route('/')
@login_required
def list_proposals():
    """
    List proposals based on user role.
    - Researchers: See their own proposals
    - Reviewers: See assigned proposals
    - HOD/Admin: See all proposals
    """
    form = ProposalFilterForm(request.args)
    
    if current_user.is_researcher():
        query = Proposal.query.filter_by(researcher_id=current_user.id)
    elif current_user.is_reviewer():
        # Reviewers see proposals assigned to them
        from app.models.review import Review
        assigned_proposal_ids = [r.proposal_id for r in Review.query.filter_by(reviewer_id=current_user.id).all()]
        query = Proposal.query.filter(Proposal.id.in_(assigned_proposal_ids))
    else:
        # HOD and Admin see all proposals
        query = Proposal.query
    
    # Apply filters
    if form.status.data:
        query = query.filter_by(status=form.status.data)
    
    if form.search.data:
        search_term = f'%{form.search.data}%'
        query = query.filter(Proposal.title.ilike(search_term))
    
    proposals = query.order_by(Proposal.created_at.desc()).all()
    
    return render_template('proposals/list.html', proposals=proposals, form=form)


@proposals_bp.route('/my')
@login_required
@role_required('researcher')
def my_proposals():
    """View researcher's own proposals."""
    proposals = Proposal.get_by_researcher(current_user.id)
    return render_template('proposals/my_proposals.html', proposals=proposals)


@proposals_bp.route('/new', methods=['GET', 'POST'])
@login_required
@role_required('researcher')
def create():
    """Create a new proposal."""
    form = ProposalForm()
    
    if form.validate_on_submit():
        proposal = Proposal(
            title=form.title.data,
            abstract=form.abstract.data,
            objectives=form.objectives.data,
            methodology=form.methodology.data,
            expected_outcomes=form.expected_outcomes.data,
            requested_amount=form.requested_amount.data,
            duration_months=form.duration_months.data,
            researcher_id=current_user.id,
            status=Proposal.STATUS_DRAFT
        )
        
        db.session.add(proposal)
        db.session.commit()
        
        flash('Proposal created successfully! You can now upload documents.', 'success')
        return redirect(url_for('proposals.view', proposal_id=proposal.id))
    
    return render_template('proposals/create.html', form=form)


@proposals_bp.route('/<int:proposal_id>')
@login_required
def view(proposal_id):
    """View proposal details."""
    proposal = Proposal.query.get_or_404(proposal_id)
    
    # Check access permissions
    if current_user.is_researcher() and proposal.researcher_id != current_user.id:
        flash('You do not have permission to view this proposal.', 'danger')
        return redirect(url_for('proposals.my_proposals'))
    
    documents = proposal.documents.filter_by(is_current=True).all()
    reviews = proposal.reviews.all() if not current_user.is_researcher() else []
    
    return render_template('proposals/view.html', 
                          proposal=proposal, 
                          documents=documents,
                          reviews=reviews)


@proposals_bp.route('/<int:proposal_id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('researcher')
def edit(proposal_id):
    """Edit a draft proposal."""
    proposal = Proposal.query.get_or_404(proposal_id)
    
    # Check ownership
    if proposal.researcher_id != current_user.id:
        flash('You do not have permission to edit this proposal.', 'danger')
        return redirect(url_for('proposals.my_proposals'))
    
    # Check if editable
    if not proposal.can_edit():
        flash('This proposal can no longer be edited.', 'warning')
        return redirect(url_for('proposals.view', proposal_id=proposal_id))
    
    form = ProposalForm(obj=proposal)
    
    if form.validate_on_submit():
        proposal.title = form.title.data
        proposal.abstract = form.abstract.data
        proposal.objectives = form.objectives.data
        proposal.methodology = form.methodology.data
        proposal.expected_outcomes = form.expected_outcomes.data
        proposal.requested_amount = form.requested_amount.data
        proposal.duration_months = form.duration_months.data
        
        db.session.commit()
        flash('Proposal updated successfully!', 'success')
        return redirect(url_for('proposals.view', proposal_id=proposal_id))
    
    return render_template('proposals/edit.html', form=form, proposal=proposal)


@proposals_bp.route('/<int:proposal_id>/submit', methods=['POST'])
@login_required
@role_required('researcher')
def submit_proposal(proposal_id):
    """Submit a proposal for review."""
    proposal = Proposal.query.get_or_404(proposal_id)
    
    # Check ownership
    if proposal.researcher_id != current_user.id:
        flash('You do not have permission to submit this proposal.', 'danger')
        return redirect(url_for('proposals.my_proposals'))
    
    # Check if can submit
    if not proposal.can_submit():
        flash('This proposal cannot be submitted. Please ensure all required fields are filled.', 'warning')
        return redirect(url_for('proposals.view', proposal_id=proposal_id))
    
    if proposal.submit():
        flash('Proposal submitted successfully! It will be reviewed shortly.', 'success')
    else:
        flash('Failed to submit proposal.', 'danger')
    
    return redirect(url_for('proposals.view', proposal_id=proposal_id))


@proposals_bp.route('/<int:proposal_id>/upload', methods=['GET', 'POST'])
@login_required
@role_required('researcher')
def upload_document(proposal_id):
    """Upload a document to a proposal."""
    proposal = Proposal.query.get_or_404(proposal_id)
    
    # Check ownership
    if proposal.researcher_id != current_user.id:
        flash('You do not have permission to upload to this proposal.', 'danger')
        return redirect(url_for('proposals.my_proposals'))
    
    # Check if editable
    if not proposal.can_edit():
        flash('Documents cannot be added to this proposal.', 'warning')
        return redirect(url_for('proposals.view', proposal_id=proposal_id))
    
    form = DocumentUploadForm()
    
    if form.validate_on_submit():
        file = form.document.data
        
        # Save the file
        saved_filename, original_filename = save_uploaded_file(file, subfolder='proposals')
        
        if saved_filename:
            # Get file info
            file_ext = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else ''
            upload_folder = current_app.config['UPLOAD_FOLDER']
            file_path = os.path.join(upload_folder, 'proposals', saved_filename)
            file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
            
            # Check for existing document of same type to version
            existing = ProposalDocument.query.filter_by(
                proposal_id=proposal_id,
                file_type=form.document_type.data,
                is_current=True
            ).first()
            
            new_version = 1
            if existing:
                existing.is_current = False
                new_version = existing.version + 1
            
            # Create document record
            document = ProposalDocument(
                proposal_id=proposal_id,
                filename=saved_filename,
                original_filename=original_filename,
                file_type=form.document_type.data,
                file_extension=file_ext,
                file_size=file_size,
                version=new_version,
                is_current=True
            )
            
            db.session.add(document)
            db.session.commit()
            
            flash(f'Document "{original_filename}" uploaded successfully!', 'success')
        else:
            flash('Failed to upload document. Please try again.', 'danger')
        
        return redirect(url_for('proposals.view', proposal_id=proposal_id))
    
    return render_template('proposals/upload.html', form=form, proposal=proposal)


@proposals_bp.route('/documents/<int:document_id>/download')
@login_required
def download_document(document_id):
    """Download a proposal document."""
    document = ProposalDocument.query.get_or_404(document_id)
    proposal = Proposal.query.get(document.proposal_id)
    
    # Check access
    if current_user.is_researcher() and proposal.researcher_id != current_user.id:
        flash('You do not have permission to download this document.', 'danger')
        return redirect(url_for('proposals.my_proposals'))
    
    upload_folder = current_app.config['UPLOAD_FOLDER']
    return send_from_directory(
        os.path.join(upload_folder, 'proposals'),
        document.filename,
        as_attachment=True,
        download_name=document.original_filename
    )


@proposals_bp.route('/documents/<int:document_id>/delete', methods=['POST'])
@login_required
@role_required('researcher')
def delete_document(document_id):
    """Delete a proposal document."""
    document = ProposalDocument.query.get_or_404(document_id)
    proposal = Proposal.query.get(document.proposal_id)
    
    # Check ownership
    if proposal.researcher_id != current_user.id:
        flash('You do not have permission to delete this document.', 'danger')
        return redirect(url_for('proposals.my_proposals'))
    
    # Check if editable
    if not proposal.can_edit():
        flash('Documents cannot be deleted from this proposal.', 'warning')
        return redirect(url_for('proposals.view', proposal_id=proposal.id))
    
    # Delete file from filesystem
    delete_uploaded_file(document.filename, subfolder='proposals')
    
    # Delete database record
    db.session.delete(document)
    db.session.commit()
    
    flash('Document deleted successfully.', 'success')
    return redirect(url_for('proposals.view', proposal_id=proposal.id))


@proposals_bp.route('/<int:proposal_id>/status')
@login_required
def status(proposal_id):
    """View detailed proposal status and history."""
    proposal = Proposal.query.get_or_404(proposal_id)
    
    # Check access
    if current_user.is_researcher() and proposal.researcher_id != current_user.id:
        flash('You do not have permission to view this proposal.', 'danger')
        return redirect(url_for('proposals.my_proposals'))
    
    reviews = proposal.reviews.all()
    avg_score = proposal.get_average_score()
    
    return render_template('proposals/status.html', 
                          proposal=proposal, 
                          reviews=reviews,
                          average_score=avg_score)
