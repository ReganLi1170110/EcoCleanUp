## GenAI Usage Acknowledgement

In accordance with COMP639 assessment guidelines, I acknowledge the use of Generative AI tools in this project.

### Tools Used
- **ChatGPT (GPT-4)** - Debugging assistance and code suggestions
- **GitHub Copilot** - Code completion during development

### How GenAI Was Used
- Debugging template errors (e.g., fixing 'now is undefined' in Flask templates)
- Generating SQL queries for event scheduling conflict detection
- Assisting with Flask route structure and role-based decorators
- README documentation structure and formatting
- Creating realistic test data for database population

### Sample Prompts Used
- "How to fix 'now is undefined' in Flask template?"
- "Generate SQL to check if a volunteer is already registered for another event at the same time"
- "Create a decorator for role-based access control in Flask"
- "Design a responsive Bootstrap navbar with sustainability theme"
- "Generate realistic test data for 20 volunteers with environmental interests"

### Reflection
All AI-generated code was reviewed, tested, and modified to ensure it met project requirements.
The final implementation, logical structure, and problem-solving approach represent my own work and understanding.
AI-generated code was always tested and adapted to fit the specific requirements of the project.

### Image reference

Unsplash. (2021). *Community cleanup volunteers* [Photograph].https://images.unsplash.com/photo-1618477461853-cf6ed80faba5

///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

# System overview 
EcoCleanUp Hub is a web-based platform designed to streamline the organization and coordination of community cleanup events. The system connects volunteers with local environmental initiatives, providing tools for event discovery, registration, participation tracking, and impact measurement.

### Key Features

**For Volunteers:**
- Browse and filter upcoming cleanup events by date, location, and event type
- Register for events with automatic scheduling conflict detection
- View personal participation history with attendance status
- Submit feedback with star ratings (1-5) and comments for attended events
- Receive pop-up reminders on login for upcoming registered events

**For Event Leaders:**
- Create new cleanup events with all required details (name, location, date, time, duration, supplies, safety instructions)
- Manage existing events (edit details, cancel events)
- View and manage registered volunteers for each event
- Track volunteer attendance during events
- Record event outcomes including bags collected and recyclables sorted
- View volunteer participation history across all managed events
- Send reminder notifications to volunteers for upcoming events
- Review all feedback submitted by volunteers

**For Administrators:**
- View all users with search and filter capabilities (by name, role, status)
- Activate or deactivate user accounts
- Access platform-wide statistics including total events, volunteers, feedback submissions, and average ratings
- Generate comprehensive event reports with attendance and engagement data

///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

# EcoCleanUp Hub - Deployment Instructions

## Local Development

1. **Clone repository**
git clone https://github.com/Reganli1170110/EcoCleanUp.git
cd EcoCleanUp


2. **Create virtual environment & install dependencies**
python -m venv venv
source venv/bin/activate # Windows: venv\Scripts\activate
pip install -r requirements.txt

3. **Configure database**
- Create a PostgreSQL database locally
- Update `connect.py` with local database credentials

4. **Run database scripts**
psql -U regan_li -d ecocleanup_db -f create_database.sql
psql -U regan_li -d ecocleanup_db -f populate_database.sql

5. **Run application**
Access at http://localhost:5000

## PythonAnywhere Deployment

1. **Clone repository** in PythonAnywhere Bash console:
git clone https://github.com/Reganli1170110/EcoCleanUp.git
cd EcoCleanUp

2. **Create virtual environment & install dependencies**
mkvirtualenv --python=/usr/bin/python3.10 ecocleanup-venv
pip install -r requirements.txt

3. **Configure database connection**
- Update `connect.py` with provided PostgreSQL credentials:
DB_HOST = 'lincolnmac-5080.postgres.pythonanywhere-services.com'
DB_PORT = 15080
DB_USER = 'regan_li'
DB_NAME = 'regan_li_ecu'
DB_PASSWORD = '#_=MT@EGS9ralW0d'

4. **Set up database**
export PGPASSWORD='#_=MT@EGS9ralW0d'
psql -h lincolnmac-5080.postgres.pythonanywhere-services.com -p 15080 -U regan_li -d regan_li_ecu -f /home/Reganli1170110/EcoCleanUp/create_database.sql
psql -h lincolnmac-5080.postgres.pythonanywhere-services.com -p 15080 -U regan_li -d regan_li_ecu -f /home/Reganli1170110/EcoCleanUp/populate_database.sql

5. **Configure Web app** in PythonAnywhere Web tab:
- Source code: `/home/Reganli1170110/EcoCleanUp`
- Working directory: `/home/Reganli1170110/EcoCleanUp`
- Virtual environment: `/home/Reganli1170110/.virtualenvs/ecocleanup-venv`
- Static files: `/static/` → `/home/Reganli1170110/EcoCleanUp/static`

6. **Update WSGI file** with:
```python
import sys
path = '/home/Reganli1170110/EcoCleanUp'
if path not in sys.path:
    sys.path.insert(0, path)
from app import app as application

Reload application and access at https://reganli1170110.pythonanywhere.com



