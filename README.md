# Research-Grant-Management-System
A web-based Research Grant Management System designed to streamline proposal submission, review, approval, grant allocation, and progress monitoring for academic institutions.

# Research Grant Management System (RGMS)
A Flask-based web application for managing research grant proposals, reviews, and approvals.
## Project Status
| Phase | Description | Status |
|-------|-------------|--------|
| Phase 1-3 | Planning, Design, Environment Setup | ✅ Complete |
| Phase 4 | User System (Login, Registration, Roles) | ✅ Complete |
| Phase 5 | Proposal System (Submit, Upload, Track) | ✅ Complete |
| Phase 6 | Review System (Assign, Evaluate, Score) | ✅ Complete |
| Phase 7 | Approval System | 🔲 To Do |
| Phase 8 | Grant Allocation System | 🔲 To Do |
| Phase 9-15 | Notifications, Reports, Extra Features | 🔲 To Do |
---
## 🚀 Quick Start
### Prerequisites
- Python 3.10 or higher
- pip (Python package manager)
### Installation
```powershell
# 1. Navigate to project folder
cd research_grant_system
# 2. Create virtual environment
py -m venv venv
# 3. Activate virtual environment
.\venv\Scripts\activate        # Windows
# source venv/bin/activate     # Linux/Mac
# 4. Install dependencies
pip install -r requirements.txt
# 5. Initialize database
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
# 6. Run development server
flask run
```
### Access the Application
Open your browser to: **http://127.0.0.1:5000**
---
## Project Structure
```
research_grant_system/
│
├── app/                          # Main application package
│   ├── __init__.py               # Flask app factory
│   ├── config.py                 # Configuration settings
│   ├── extensions.py             # Flask extensions (SQLAlchemy, Login, etc.)
│   │
│   ├── models/                   # Database models
│   │   ├── __init__.py
│   │   ├── user.py               # User model with roles
│   │   ├── proposal.py           # Proposal & ProposalDocument models
│   │   └── review.py             # Review model
│   │
│   ├── routes/                   # View routes (Blueprints)
│   │   ├── __init__.py
│   │   ├── main.py               # Home, dashboards
│   │   ├── auth.py               # Login, register, profile
│   │   ├── proposals.py          # Proposal CRUD operations
│   │   └── reviews.py            # Review assignment & evaluation
│   │
│   ├── forms/                    # WTForms for validation
│   │   ├── __init__.py
│   │   ├── auth_forms.py         # Login, Register, Profile forms
│   │   ├── proposal_forms.py     # Proposal submission forms
│   │   └── review_forms.py       # Review evaluation forms
│   │
│   ├── utils/                    # Utility functions
│   │   ├── __init__.py
│   │   ├── decorators.py         # Role-based access decorators
│   │   └── helpers.py            # File upload, helpers
│   │
│   ├── templates/                # Jinja2 HTML templates
│   │   ├── base.html             # Base layout
│   │   ├── index.html            # Home page
│   │   ├── auth/                 # Login, register, profile pages
│   │   ├── proposals/            # Proposal pages
│   │   ├── reviews/              # Review pages
│   │   ├── researcher/           # Researcher dashboard
│   │   ├── reviewer/             # Reviewer dashboard
│   │   ├── hod/                  # HOD dashboard
│   │   ├── admin/                # Admin dashboard
│   │   └── errors/               # Error pages (403, 404, 500)
│   │
│   └── static/                   # Static assets
│       ├── css/style.css
│       └── js/main.js
│
├── migrations/                   # Database migrations (Alembic)
├── instance/                     # Instance folder (database file)
├── requirements.txt              # Python dependencies
├── run.py                        # Application entry point
├── .env                          # Environment variables
└── .gitignore                    # Git ignore file
```
---
## User Roles
| Role | Permissions |
|------|-------------|
| **Researcher** | Create/submit proposals, upload documents, track status |
| **Reviewer** | Evaluate assigned proposals, provide scores & feedback |
| **HOD** | Assign reviewers, view all proposals, approve/reject |
| **Admin** | Full system access, manage users, view reports |
---
## Database Models
### User
- `id`, `email`, `username`, `password_hash`
- `role` (researcher/reviewer/hod/admin)
- `full_name`, `department`, `phone`
- `is_active`, `created_at`
### Proposal
- `id`, `title`, `abstract`, `objectives`, `methodology`
- `requested_amount`, `duration_months`
- `status` (draft → submitted → under_review → reviewed → approved/rejected → funded)
- `researcher_id` (FK to User)
### ProposalDocument
- `id`, `proposal_id`, `filename`, `original_filename`
- `file_type`, `file_size`, `version`
### Review
- `id`, `proposal_id`, `reviewer_id`
- `score`, `technical_merit`, `feasibility`, `impact`, `budget_appropriateness`
- `comments`, `strengths`, `weaknesses`, `suggestions`
- `recommendation` (approve/reject/revise)
- `status` (pending/in_progress/completed)
---
## Tech Stack
- **Backend:** Flask 3.0, Flask-SQLAlchemy, Flask-Login, Flask-WTF, Flask-Migrate
- **Database:** SQLite (development), can switch to PostgreSQL/MySQL
- **Frontend:** Bootstrap 5, Bootstrap Icons, Jinja2 templates
- **Forms:** WTForms with CSRF protection
---
## Remaining Phases (TODO)
### Phase 7: Approval System
- [ ] Create Approval model
- [ ] Build HOD approval workflow
- [ ] Implement approval/rejection with comments
- [ ] Add approval history tracking
### Phase 8: Grant Allocation System
- [ ] Create Grant model
- [ ] Build fund allocation feature
- [ ] Implement budget tracking
- [ ] Add disbursement records
### Phase 9: Notification System
- [ ] Email notifications
- [ ] In-app notifications
- [ ] Status change alerts
### Phase 10-15: Additional Features
- [ ] Reporting and analytics
- [ ] Advanced search/filtering
- [ ] Document versioning
- [ ] Audit logs
- [ ] User management (admin)
- [ ] System settings
---
## Configuration
Environment variables in `.env`:
```
FLASK_APP=run.py
FLASK_DEBUG=1
SECRET_KEY=your-secret-key-change-in-production
DATABASE_URL=sqlite:///rgms.db
```
---
## Adding New Features
### 1. Create a new model (e.g., `app/models/grant.py`):
```python
from app.extensions import db
from datetime import datetime
class Grant(db.Model):
    __tablename__ = 'grants'
    id = db.Column(db.Integer, primary_key=True)
    # Add fields...
```
### 2. Import in `app/models/__init__.py`
### 3. Create forms in `app/forms/`
### 4. Create routes in `app/routes/`
### 5. Register blueprint in `app/__init__.py`
### 6. Create templates in `app/templates/`
### 7. Run migrations:
```powershell
flask db migrate -m "Add grant model"
flask db upgrade
```
---
## Team
- **Phases 4-6:** [Your Name]
- **Phase 7+:** [Team Member Names]
---
## License
This project is for educational purposes.
