"""
Review Forms - Phase 6
Forms for proposal review, scoring, and reviewer assignment.
"""
from flask_wtf import FlaskForm
from wtforms import TextAreaField, IntegerField, SelectField, SubmitField, DateTimeLocalField
from wtforms.validators import DataRequired, NumberRange, Optional, Length


class ReviewForm(FlaskForm):
    """Form for reviewers to evaluate proposals."""
    
    # Scoring fields (1-10 scale)
    technical_merit = IntegerField('Technical Merit (1-10)', validators=[
        DataRequired(message='Technical merit score is required'),
        NumberRange(min=1, max=10, message='Score must be between 1 and 10')
    ])
    feasibility = IntegerField('Feasibility (1-10)', validators=[
        DataRequired(message='Feasibility score is required'),
        NumberRange(min=1, max=10, message='Score must be between 1 and 10')
    ])
    impact = IntegerField('Potential Impact (1-10)', validators=[
        DataRequired(message='Impact score is required'),
        NumberRange(min=1, max=10, message='Score must be between 1 and 10')
    ])
    budget_appropriateness = IntegerField('Budget Appropriateness (1-10)', validators=[
        DataRequired(message='Budget appropriateness score is required'),
        NumberRange(min=1, max=10, message='Score must be between 1 and 10')
    ])
    
    # Overall score (calculated or manual)
    score = IntegerField('Overall Score (1-10)', validators=[
        DataRequired(message='Overall score is required'),
        NumberRange(min=1, max=10, message='Score must be between 1 and 10')
    ])
    
    # Feedback
    strengths = TextAreaField('Strengths', validators=[
        Optional(),
        Length(max=2000, message='Strengths must be less than 2000 characters')
    ])
    weaknesses = TextAreaField('Weaknesses', validators=[
        Optional(),
        Length(max=2000, message='Weaknesses must be less than 2000 characters')
    ])
    comments = TextAreaField('General Comments', validators=[
        DataRequired(message='Please provide comments'),
        Length(min=50, max=5000, message='Comments must be between 50 and 5000 characters')
    ])
    suggestions = TextAreaField('Suggestions for Improvement', validators=[
        Optional(),
        Length(max=2000, message='Suggestions must be less than 2000 characters')
    ])
    
    # Recommendation
    recommendation = SelectField('Recommendation', validators=[
        DataRequired(message='Please select a recommendation')
    ], choices=[
        ('', 'Select Recommendation'),
        ('approve', 'Recommend Approval'),
        ('revise', 'Requires Revision'),
        ('reject', 'Recommend Rejection')
    ])
    
    submit = SubmitField('Submit Review')
    save_draft = SubmitField('Save as Draft')


class QuickReviewForm(FlaskForm):
    """Simplified review form for quick evaluations."""
    score = IntegerField('Overall Score (1-10)', validators=[
        DataRequired(message='Score is required'),
        NumberRange(min=1, max=10, message='Score must be between 1 and 10')
    ])
    comments = TextAreaField('Comments', validators=[
        DataRequired(message='Please provide comments'),
        Length(min=20, max=2000, message='Comments must be between 20 and 2000 characters')
    ])
    recommendation = SelectField('Recommendation', validators=[
        DataRequired(message='Please select a recommendation')
    ], choices=[
        ('', 'Select...'),
        ('approve', 'Approve'),
        ('revise', 'Needs Revision'),
        ('reject', 'Reject')
    ])
    submit = SubmitField('Submit Review')


class AssignReviewerForm(FlaskForm):
    """Form for assigning reviewers to proposals."""
    reviewer_id = SelectField('Select Reviewer', validators=[
        DataRequired(message='Please select a reviewer')
    ], coerce=int)
    deadline = DateTimeLocalField('Review Deadline', validators=[
        Optional()
    ], format='%Y-%m-%dT%H:%M')
    submit = SubmitField('Assign Reviewer')
    
    def __init__(self, *args, **kwargs):
        """Initialize form with reviewer choices."""
        super(AssignReviewerForm, self).__init__(*args, **kwargs)
        # Choices will be set dynamically in the route
        self.reviewer_id.choices = []


class ReviewFilterForm(FlaskForm):
    """Form for filtering reviews list."""
    status = SelectField('Status', choices=[
        ('', 'All Statuses'),
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed')
    ], default='')
    submit = SubmitField('Filter')
