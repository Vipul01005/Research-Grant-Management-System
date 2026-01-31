"""
Proposal Forms - Phase 5
Forms for proposal submission and document upload.
"""
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, TextAreaField, FloatField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Optional


class ProposalForm(FlaskForm):
    """Form for creating/editing proposals."""
    title = StringField('Proposal Title', validators=[
        DataRequired(message='Title is required'),
        Length(min=10, max=255, message='Title must be between 10 and 255 characters')
    ])
    abstract = TextAreaField('Abstract', validators=[
        DataRequired(message='Abstract is required'),
        Length(min=100, max=5000, message='Abstract must be between 100 and 5000 characters')
    ])
    objectives = TextAreaField('Research Objectives', validators=[
        Optional(),
        Length(max=5000, message='Objectives must be less than 5000 characters')
    ])
    methodology = TextAreaField('Methodology', validators=[
        Optional(),
        Length(max=5000, message='Methodology must be less than 5000 characters')
    ])
    expected_outcomes = TextAreaField('Expected Outcomes', validators=[
        Optional(),
        Length(max=3000, message='Expected outcomes must be less than 3000 characters')
    ])
    requested_amount = FloatField('Requested Amount ($)', validators=[
        DataRequired(message='Requested amount is required'),
        NumberRange(min=1, max=10000000, message='Amount must be between $1 and $10,000,000')
    ])
    duration_months = IntegerField('Duration (months)', validators=[
        DataRequired(message='Duration is required'),
        NumberRange(min=1, max=60, message='Duration must be between 1 and 60 months')
    ], default=12)
    
    submit = SubmitField('Save Draft')
    submit_for_review = SubmitField('Submit for Review')


class DocumentUploadForm(FlaskForm):
    """Form for uploading documents to a proposal."""
    document = FileField('Select Document', validators=[
        FileRequired(message='Please select a file'),
        FileAllowed(['pdf', 'doc', 'docx', 'txt'], 
                   'Only PDF, DOC, DOCX, and TXT files are allowed')
    ])
    document_type = SelectField('Document Type', choices=[
        ('proposal', 'Proposal Document'),
        ('budget', 'Budget Breakdown'),
        ('cv', 'Curriculum Vitae'),
        ('supporting', 'Supporting Document'),
        ('other', 'Other')
    ], default='proposal')
    submit = SubmitField('Upload Document')


class ProposalFilterForm(FlaskForm):
    """Form for filtering proposals list."""
    status = SelectField('Status', choices=[
        ('', 'All Statuses'),
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('reviewed', 'Reviewed'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('funded', 'Funded')
    ], default='')
    search = StringField('Search', validators=[
        Optional(),
        Length(max=100)
    ])
    submit = SubmitField('Filter')
