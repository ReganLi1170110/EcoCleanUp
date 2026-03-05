"""
EcoCleanUp Hub - Main Application
COMP639 Individual Project
Student: Regan Li
Student ID: 1170110
"""

from flask import Flask, render_template, redirect, url_for, request, session, flash, g
from flask_bcrypt import Bcrypt
import psycopg2
import psycopg2.extras
import os
import sys
from functools import wraps
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'ecocleanup-secret-key-2026'
bcrypt = Bcrypt(app)

# Configuration for file uploads
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Database connection function
def get_db_connection():
    """Establish connection to PostgreSQL database"""
    try:
        from connect import DB_HOST, DB_PORT, DB_USER, DB_NAME, DB_PASSWORD

        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

# Login required decorator
def login_required(f):
    """Decorator to require login for route access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Role required decorator
def role_required(*roles):
    """Decorator to restrict access based on user role"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'role' not in session or session['role'] not in roles:
                flash('You do not have permission to access this page', 'danger')
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Helper function to check allowed file extensions
def allowed_file(filename):
    """Check if uploaded file has an allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Helper function to get user notifications
def get_user_notifications(user_id, role):
    """Retrieve unread notifications for the current user"""
    conn = get_db_connection()
    if not conn:
        return []

    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        # Get all notifications for the user (both read and unread)
        cur.execute("""
            SELECT e.event_id, e.event_name, e.event_date, e.event_time, e.location,
                   n.notification_id, n.message, n.sent_date, n.is_read
            FROM notifications n
            JOIN events e ON n.event_id = e.event_id
            WHERE n.user_id = %s
            ORDER BY n.sent_date DESC
        """, (user_id,))

        return cur.fetchall()
    except Exception as e:
        print(f"Error getting notifications: {e}")
        return []
    finally:
        cur.close()
        conn.close()

# Before request - check if user is active and get notifications
@app.before_request
def before_request():
    """Execute before each request to set up user context and notifications"""
    g.user = None
    g.notifications = []
    if 'user_id' in session:
        conn = get_db_connection()
        if conn:
            try:
                cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
                cur.execute("SELECT user_id, username, role, status, profile_image FROM users WHERE user_id = %s",
                           (session['user_id'],))
                user = cur.fetchone()

                if user and user['status'] == 'inactive':
                    # Deactivate session if user is inactive
                    session.clear()
                    flash('Your account has been deactivated. Please contact an administrator.', 'danger')
                elif user:
                    g.user = dict(user)
                    session['profile_image'] = user['profile_image']

                    # Get notifications for the user
                    g.notifications = get_user_notifications(session['user_id'], session['role'])
                else:
                    session.clear()
            except Exception as e:
                print(f"Error in before_request: {e}")
                session.clear()
            finally:
                cur.close()
                conn.close()

# Routes
@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page - all users login here"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        if conn:
            try:
                cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
                cur.execute("""
                    SELECT user_id, username, password_hash, role, status, profile_image
                    FROM users WHERE username = %s
                """, (username,))
                user = cur.fetchone()

                if user and bcrypt.check_password_hash(user['password_hash'], password):
                    if user['status'] == 'active':
                        session['user_id'] = user['user_id']
                        session['username'] = user['username']
                        session['role'] = user['role']
                        session['profile_image'] = user['profile_image']

                        flash(f'Welcome back, {user["username"]}!', 'success')

                        # Redirect based on role
                        if user['role'] == 'volunteer':
                            return redirect(url_for('volunteer_dashboard'))
                        elif user['role'] == 'event_leader':
                            return redirect(url_for('event_leader_dashboard'))
                        elif user['role'] == 'admin':
                            return redirect(url_for('admin_dashboard'))
                    else:
                        flash('Your account is inactive. Please contact an administrator.', 'danger')
                else:
                    flash('Invalid username or password', 'danger')
            except Exception as e:
                flash(f'Login error: {e}', 'danger')
            finally:
                cur.close()
                conn.close()
        else:
            flash('Database connection error', 'danger')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Registration page - only for volunteers"""
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        full_name = request.form['full_name']
        home_address = request.form['home_address']
        contact_number = request.form['contact_number']
        environmental_interests = request.form['environmental_interests']

        # Validation
        errors = []

        # Check if passwords match
        if password != confirm_password:
            errors.append('Passwords do not match')

        # Check password length
        if len(password) < 8:
            errors.append('Password must be at least 8 characters long')

        # Check password complexity
        if not any(c.isupper() for c in password):
            errors.append('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in password):
            errors.append('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in password):
            errors.append('Password must contain at least one number')

        # Handle profile image upload
        profile_image = 'default_profile.png'
        if 'profile_image' in request.files:
            file = request.files['profile_image']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(f"{username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                profile_image = filename

        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('register.html', form_data=request.form)

        conn = get_db_connection()
        if conn:
            try:
                cur = conn.cursor()

                # Check if username already exists
                cur.execute("SELECT user_id FROM users WHERE username = %s", (username,))
                if cur.fetchone():
                    flash('Username already exists. Please choose another.', 'danger')
                    return render_template('register.html', form_data=request.form)

                # Check if email already exists
                cur.execute("SELECT user_id FROM users WHERE email = %s", (email,))
                if cur.fetchone():
                    flash('Email already registered. Please use another email.', 'danger')
                    return render_template('register.html', form_data=request.form)

                # Hash password
                password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

                # Insert new user (always as volunteer)
                cur.execute("""
                    INSERT INTO users
                    (username, email, password_hash, role, status, full_name, home_address,
                     contact_number, environmental_interests, profile_image)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (username, email, password_hash, 'volunteer', 'active',
                      full_name, home_address, contact_number, environmental_interests, profile_image))

                conn.commit()
                flash('Registration successful! Please log in.', 'success')
                return redirect(url_for('login'))

            except Exception as e:
                conn.rollback()
                flash(f'Registration error: {e}', 'danger')
            finally:
                cur.close()
                conn.close()
        else:
            flash('Database connection error', 'danger')

    return render_template('register.html')

@app.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

# ==================== NOTIFICATION ROUTES ====================

@app.route('/notifications/mark-read', methods=['POST'])
@login_required
def mark_notifications_read():
    """Mark all notifications as read for the current user"""
    conn = get_db_connection()
    if not conn:
        return {'success': False, 'error': 'Database connection error'}

    try:
        cur = conn.cursor()
        cur.execute("""
            UPDATE notifications
            SET is_read = TRUE
            WHERE user_id = %s AND is_read = FALSE
        """, (session['user_id'],))
        conn.commit()

        # Get updated unread count
        cur.execute("""
            SELECT COUNT(*) as count
            FROM notifications
            WHERE user_id = %s AND is_read = FALSE
        """, (session['user_id'],))
        count = cur.fetchone()[0]

        return {'success': True, 'unread_count': count}
    except Exception as e:
        return {'success': False, 'error': str(e)}
    finally:
        cur.close()
        conn.close()

# ==================== VOLUNTEER ROUTES ====================

@app.route('/volunteer/dashboard')
@login_required
@role_required('volunteer')
def volunteer_dashboard():
    """Volunteer dashboard"""
    conn = get_db_connection()
    if not conn:
        flash('Database connection error', 'danger')
        return redirect(url_for('index'))

    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        # Get upcoming events the volunteer is registered for
        cur.execute("""
            SELECT e.event_id, e.event_name, e.location, e.event_date, e.event_time,
                   e.duration, e.supplies, e.safety_instructions, r.status
            FROM events e
            JOIN registrations r ON e.event_id = r.event_id
            WHERE r.user_id = %s AND e.event_date >= CURRENT_DATE
            ORDER BY e.event_date, e.event_time
            LIMIT 5
        """, (session['user_id'],))
        upcoming_events = cur.fetchall()

        # Get recent past events
        cur.execute("""
            SELECT e.event_id, e.event_name, e.location, e.event_date, e.event_time,
                   r.status, r.attendance_status, r.feedback_rating
            FROM events e
            JOIN registrations r ON e.event_id = r.event_id
            WHERE r.user_id = %s AND e.event_date < CURRENT_DATE
            ORDER BY e.event_date DESC
            LIMIT 5
        """, (session['user_id'],))
        past_events = cur.fetchall()

        # Get total participation count
        cur.execute("""
            SELECT COUNT(*) as total
            FROM registrations
            WHERE user_id = %s AND attendance_status = 'attended'
        """, (session['user_id'],))
        total_participated = cur.fetchone()['total']

        return render_template('volunteer/dashboard.html',
                              upcoming_events=upcoming_events,
                              past_events=past_events,
                              total_participated=total_participated)
    except Exception as e:
        flash(f'Error loading dashboard: {e}', 'danger')
        return redirect(url_for('index'))
    finally:
        cur.close()
        conn.close()

@app.route('/volunteer/events')
@login_required
@role_required('volunteer')
def volunteer_events():
    """Browse all upcoming events with filters"""
    conn = get_db_connection()
    if not conn:
        flash('Database connection error', 'danger')
        return redirect(url_for('volunteer_dashboard'))

    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        # Get filter parameters
        date_filter = request.args.get('date', '')
        location_filter = request.args.get('location', '')
        event_type_filter = request.args.get('event_type', '')

        # Base query
        query = """
            SELECT e.event_id, e.event_name, e.location, e.event_date, e.event_time,
                   e.duration, e.supplies, e.safety_instructions, e.event_type,
                   (SELECT COUNT(*) FROM registrations WHERE event_id = e.event_id AND status = 'registered') as registered_count,
                   CASE WHEN r.user_id IS NOT NULL THEN TRUE ELSE FALSE END as is_registered
            FROM events e
            LEFT JOIN registrations r ON e.event_id = r.event_id AND r.user_id = %s
            WHERE e.event_date >= CURRENT_DATE
        """
        params = [session['user_id']]

        # Apply filters
        if date_filter:
            query += " AND e.event_date = %s"
            params.append(date_filter)

        if location_filter:
            query += " AND e.location ILIKE %s"
            params.append(f'%{location_filter}%')

        if event_type_filter:
            query += " AND e.event_type = %s"
            params.append(event_type_filter)

        query += " ORDER BY e.event_date, e.event_time"

        cur.execute(query, params)
        events = cur.fetchall()

        # Get distinct locations for filter dropdown
        cur.execute("SELECT DISTINCT location FROM events WHERE event_date >= CURRENT_DATE ORDER BY location")
        locations = cur.fetchall()

        return render_template('volunteer/events.html',
                              events=events,
                              locations=locations,
                              current_filters={'date': date_filter, 'location': location_filter, 'event_type': event_type_filter})
    except Exception as e:
        flash(f'Error loading events: {e}', 'danger')
        return redirect(url_for('volunteer_dashboard'))
    finally:
        cur.close()
        conn.close()

@app.route('/volunteer/event/<int:event_id>')
@login_required
@role_required('volunteer')
def volunteer_event_detail(event_id):
    """View event details"""
    from datetime import datetime
    now = datetime.now()

    conn = get_db_connection()
    if not conn:
        flash('Database connection error', 'danger')
        return redirect(url_for('volunteer_events'))

    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        # Get event details
        cur.execute("""
            SELECT e.*, u.full_name as leader_name,
                   (SELECT COUNT(*) FROM registrations WHERE event_id = e.event_id AND status = 'registered') as registered_count,
                   CASE WHEN r.user_id IS NOT NULL THEN TRUE ELSE FALSE END as is_registered,
                   r.status as registration_status
            FROM events e
            JOIN users u ON e.created_by = u.user_id
            LEFT JOIN registrations r ON e.event_id = r.event_id AND r.user_id = %s
            WHERE e.event_id = %s
        """, (session['user_id'], event_id))

        event = cur.fetchone()

        if not event:
            flash('Event not found', 'danger')
            return redirect(url_for('volunteer_events'))

        return render_template('volunteer/event_detail.html',
                              event=event,
                              now=now)
    except Exception as e:
        flash(f'Error loading event details: {e}', 'danger')
        return redirect(url_for('volunteer_events'))
    finally:
        cur.close()
        conn.close()

@app.route('/volunteer/register_event/<int:event_id>', methods=['POST'])
@login_required
@role_required('volunteer')
def volunteer_register_event(event_id):
    """Register for an event"""
    conn = get_db_connection()
    if not conn:
        flash('Database connection error', 'danger')
        return redirect(url_for('volunteer_events'))

    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        # Check if event exists and is upcoming
        cur.execute("""
            SELECT event_id, event_name, event_date, event_time
            FROM events
            WHERE event_id = %s AND event_date >= CURRENT_DATE
        """, (event_id,))
        event = cur.fetchone()

        if not event:
            flash('Event not found or has already passed', 'danger')
            return redirect(url_for('volunteer_events'))

        # Check if already registered
        cur.execute("""
            SELECT registration_id FROM registrations
            WHERE user_id = %s AND event_id = %s
        """, (session['user_id'], event_id))

        if cur.fetchone():
            flash('You are already registered for this event', 'warning')
            return redirect(url_for('volunteer_event_detail', event_id=event_id))

        # Check for time conflicts with other registered events
        cur.execute("""
            SELECT e.event_name, e.event_date, e.event_time
            FROM events e
            JOIN registrations r ON e.event_id = r.event_id
            WHERE r.user_id = %s
            AND r.status = 'registered'
            AND e.event_date = %s
            AND e.event_time = %s
        """, (session['user_id'], event['event_date'], event['event_time']))

        conflict = cur.fetchone()

        if conflict:
            flash(f'You are already registered for "{conflict["event_name"]}" at the same time. Registration declined.', 'danger')
            return redirect(url_for('volunteer_event_detail', event_id=event_id))

        # Register for the event
        cur.execute("""
            INSERT INTO registrations (user_id, event_id, registration_date, status)
            VALUES (%s, %s, CURRENT_TIMESTAMP, 'registered')
        """, (session['user_id'], event_id))

        conn.commit()
        flash(f'Successfully registered for {event["event_name"]}!', 'success')

    except Exception as e:
        conn.rollback()
        flash(f'Registration error: {e}', 'danger')
    finally:
        cur.close()
        conn.close()

    return redirect(url_for('volunteer_event_detail', event_id=event_id))

@app.route('/volunteer/participation_history')
@login_required
@role_required('volunteer')
def volunteer_participation_history():
    """View participation history"""
    from datetime import datetime
    now = datetime.now()

    conn = get_db_connection()
    if not conn:
        flash('Database connection error', 'danger')
        return redirect(url_for('volunteer_dashboard'))

    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        # Get all events with participation details
        cur.execute("""
            SELECT e.event_id, e.event_name, e.location, e.event_date, e.event_time,
                   r.status, r.attendance_status, r.feedback_rating, r.feedback_comment,
                   r.feedback_date
            FROM events e
            JOIN registrations r ON e.event_id = r.event_id
            WHERE r.user_id = %s
            ORDER BY e.event_date DESC
        """, (session['user_id'],))

        participations = cur.fetchall()

        # Debug print
        print(f"Found {len(participations)} participations", file=sys.stderr)
        for p in participations:
            print(f"Event: {p['event_name']}, Date: {p['event_date']}, Attended: {p['attendance_status']}, Rated: {p['feedback_rating']}", file=sys.stderr)

        return render_template('volunteer/participation_history.html',
                              participations=participations,
                              now=now)
    except Exception as e:
        flash(f'Error loading participation history: {e}', 'danger')
        return redirect(url_for('volunteer_dashboard'))
    finally:
        cur.close()
        conn.close()

@app.route('/volunteer/feedback/<int:event_id>', methods=['GET', 'POST'])
@login_required
@role_required('volunteer')
def volunteer_feedback(event_id):
    """Submit feedback for an event"""
    from datetime import datetime
    now = datetime.now()

    conn = get_db_connection()
    if not conn:
        flash('Database connection error', 'danger')
        return redirect(url_for('volunteer_participation_history'))

    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        # Get event details first - this will also verify the event exists
        cur.execute("""
            SELECT e.event_id, e.event_name, e.event_date
            FROM events e
            JOIN registrations r ON e.event_id = r.event_id
            WHERE r.user_id = %s AND e.event_id = %s
        """, (session['user_id'], event_id))

        event = cur.fetchone()

        if not event:
            flash('Event not found or you are not registered for this event', 'danger')
            return redirect(url_for('volunteer_participation_history'))

        # Check if already submitted feedback
        cur.execute("""
            SELECT registration_id FROM registrations
            WHERE user_id = %s AND event_id = %s AND feedback_rating IS NOT NULL
        """, (session['user_id'], event_id))

        if cur.fetchone():
            flash('You have already submitted feedback for this event', 'warning')
            return redirect(url_for('volunteer_participation_history'))

        # Check if volunteer attended this event
        cur.execute("""
            SELECT attendance_status FROM registrations
            WHERE user_id = %s AND event_id = %s
        """, (session['user_id'], event_id))

        reg = cur.fetchone()
        if not reg or reg['attendance_status'] != 'attended':
            flash('You can only provide feedback for events you attended', 'danger')
            return redirect(url_for('volunteer_participation_history'))

        if request.method == 'POST':
            rating = request.form['rating']
            comment = request.form['comment']

            cur.execute("""
                UPDATE registrations
                SET feedback_rating = %s, feedback_comment = %s, feedback_date = CURRENT_TIMESTAMP
                WHERE user_id = %s AND event_id = %s
            """, (rating, comment, session['user_id'], event_id))

            conn.commit()
            flash('Thank you for your feedback!', 'success')
            return redirect(url_for('volunteer_participation_history'))

        # GET request - show feedback form
        return render_template('volunteer/feedback.html', event=event, now=now)

    except Exception as e:
        flash(f'Error processing feedback: {e}', 'danger')
        return redirect(url_for('volunteer_participation_history'))
    finally:
        cur.close()
        conn.close()

# ==================== EVENT LEADER ROUTES ====================

@app.route('/event_leader/dashboard')
@login_required
@role_required('event_leader')
def event_leader_dashboard():
    """Event leader dashboard"""
    conn = get_db_connection()
    if not conn:
        flash('Database connection error', 'danger')
        return redirect(url_for('index'))

    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        # Get upcoming events created by this leader
        cur.execute("""
            SELECT event_id, event_name, location, event_date, event_time,
                   (SELECT COUNT(*) FROM registrations WHERE event_id = events.event_id AND status = 'registered') as registered_count
            FROM events
            WHERE created_by = %s AND event_date >= CURRENT_DATE AND status = 'upcoming'
            ORDER BY event_date, event_time
            LIMIT 5
        """, (session['user_id'],))
        upcoming_events = cur.fetchall()

        # Get recent completed events
        cur.execute("""
            SELECT event_id, event_name, location, event_date,
                   (SELECT COUNT(*) FROM registrations WHERE event_id = events.event_id AND attendance_status = 'attended') as attended_count,
                   bags_collected, recyclables_sorted
            FROM events
            WHERE created_by = %s AND (event_date < CURRENT_DATE OR status = 'completed')
            ORDER BY event_date DESC
            LIMIT 5
        """, (session['user_id'],))
        past_events = cur.fetchall()

        # Get statistics
        cur.execute("""
            SELECT
                COUNT(*) as total_events,
                SUM((SELECT COUNT(*) FROM registrations WHERE event_id = events.event_id)) as total_registrations,
                SUM(bags_collected) as total_bags,
                SUM(recyclables_sorted) as total_recyclables
            FROM events
            WHERE created_by = %s
        """, (session['user_id'],))
        stats = cur.fetchone()

        return render_template('event_leader/dashboard.html',
                              upcoming_events=upcoming_events,
                              past_events=past_events,
                              stats=stats)
    except Exception as e:
        flash(f'Error loading dashboard: {e}', 'danger')
        return redirect(url_for('index'))
    finally:
        cur.close()
        conn.close()

@app.route('/event_leader/create_event', methods=['GET', 'POST'])
@login_required
@role_required('event_leader')
def event_leader_create_event():
    """Create a new cleanup event"""
    from datetime import datetime
    now = datetime.now()

    if request.method == 'POST':
        event_name = request.form['event_name']
        location = request.form['location']
        event_date = request.form['event_date']
        event_time = request.form['event_time']
        duration = request.form['duration']
        supplies = request.form['supplies']
        safety_instructions = request.form['safety_instructions']
        event_type = request.form.get('event_type', 'general')

        conn = get_db_connection()
        if conn:
            try:
                cur = conn.cursor()

                cur.execute("""
                    INSERT INTO events
                    (event_name, location, event_date, event_time, duration,
                     supplies, safety_instructions, created_by, event_type)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING event_id
                """, (event_name, location, event_date, event_time, duration,
                      supplies, safety_instructions, session['user_id'], event_type))

                event_id = cur.fetchone()[0]
                conn.commit()

                flash('Event created successfully!', 'success')
                return redirect(url_for('event_leader_manage_events'))

            except Exception as e:
                conn.rollback()
                flash(f'Error creating event: {e}', 'danger')
            finally:
                cur.close()
                conn.close()
        else:
            flash('Database connection error', 'danger')

    return render_template('event_leader/create_event.html', now=now)

@app.route('/event_leader/manage_events')
@login_required
@role_required('event_leader')
def event_leader_manage_events():
    """Manage existing events"""
    from datetime import datetime
    now = datetime.now()

    conn = get_db_connection()
    if not conn:
        flash('Database connection error', 'danger')
        return redirect(url_for('event_leader_dashboard'))

    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        # Get all events created by this leader
        cur.execute("""
            SELECT event_id, event_name, location, event_date, event_time, status,
                   (SELECT COUNT(*) FROM registrations WHERE event_id = events.event_id) as registered_count,
                   bags_collected, recyclables_sorted
            FROM events
            WHERE created_by = %s
            ORDER BY event_date DESC
        """, (session['user_id'],))

        events = cur.fetchall()

        return render_template('event_leader/manage_events.html', events=events, now=now)
    except Exception as e:
        flash(f'Error loading events: {e}', 'danger')
        return redirect(url_for('event_leader_dashboard'))
    finally:
        cur.close()
        conn.close()

@app.route('/event_leader/edit_event/<int:event_id>', methods=['GET', 'POST'])
@login_required
@role_required('event_leader')
def event_leader_edit_event(event_id):
    """Edit an event"""
    from datetime import datetime
    now = datetime.now()

    conn = get_db_connection()
    if not conn:
        flash('Database connection error', 'danger')
        return redirect(url_for('event_leader_manage_events'))

    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        # Get event details
        cur.execute("""
            SELECT * FROM events
            WHERE event_id = %s AND created_by = %s
        """, (event_id, session['user_id']))

        event = cur.fetchone()

        if not event:
            flash('Event not found or you do not have permission to edit it', 'danger')
            return redirect(url_for('event_leader_manage_events'))

        if request.method == 'POST':
            event_name = request.form['event_name']
            location = request.form['location']
            event_date = request.form['event_date']
            event_time = request.form['event_time']
            duration = request.form['duration']
            supplies = request.form['supplies']
            safety_instructions = request.form['safety_instructions']
            status = request.form['status']

            cur.execute("""
                UPDATE events
                SET event_name = %s, location = %s, event_date = %s, event_time = %s,
                    duration = %s, supplies = %s, safety_instructions = %s, status = %s
                WHERE event_id = %s
            """, (event_name, location, event_date, event_time, duration,
                  supplies, safety_instructions, status, event_id))

            conn.commit()
            flash('Event updated successfully!', 'success')
            return redirect(url_for('event_leader_manage_events'))

        return render_template('event_leader/edit_event.html', event=event, now=now)

    except Exception as e:
        flash(f'Error editing event: {e}', 'danger')
        return redirect(url_for('event_leader_manage_events'))
    finally:
        cur.close()
        conn.close()

@app.route('/event_leader/cancel_event/<int:event_id>', methods=['POST'])
@login_required
@role_required('event_leader')
def event_leader_cancel_event(event_id):
    """Cancel an event"""
    conn = get_db_connection()
    if not conn:
        flash('Database connection error', 'danger')
        return redirect(url_for('event_leader_manage_events'))

    try:
        cur = conn.cursor()

        # Check if event belongs to this leader
        cur.execute("""
            SELECT event_id FROM events
            WHERE event_id = %s AND created_by = %s
        """, (event_id, session['user_id']))

        if not cur.fetchone():
            flash('Event not found or you do not have permission to cancel it', 'danger')
            return redirect(url_for('event_leader_manage_events'))

        # Update event status to cancelled
        cur.execute("""
            UPDATE events
            SET status = 'cancelled'
            WHERE event_id = %s
        """, (event_id,))

        # Update all registrations for this event
        cur.execute("""
            UPDATE registrations
            SET status = 'cancelled'
            WHERE event_id = %s
        """, (event_id,))

        conn.commit()
        flash('Event cancelled successfully', 'success')

    except Exception as e:
        conn.rollback()
        flash(f'Error cancelling event: {e}', 'danger')
    finally:
        cur.close()
        conn.close()

    return redirect(url_for('event_leader_manage_events'))

@app.route('/event_leader/event_volunteers/<int:event_id>')
@login_required
@role_required('event_leader')
def event_leader_event_volunteers(event_id):
    """View volunteers registered for an event"""
    from datetime import datetime
    now = datetime.now()

    conn = get_db_connection()
    if not conn:
        flash('Database connection error', 'danger')
        return redirect(url_for('event_leader_manage_events'))

    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        # Get event details
        cur.execute("""
            SELECT event_id, event_name, event_date, event_time, location
            FROM events
            WHERE event_id = %s AND created_by = %s
        """, (event_id, session['user_id']))

        event = cur.fetchone()

        if not event:
            flash('Event not found or you do not have permission to view it', 'danger')
            return redirect(url_for('event_leader_manage_events'))

        # Get volunteers registered for this event
        cur.execute("""
            SELECT u.user_id, u.username, u.full_name, u.email, u.contact_number,
                   r.registration_date, r.status, r.attendance_status
            FROM users u
            JOIN registrations r ON u.user_id = r.user_id
            WHERE r.event_id = %s
            ORDER BY u.full_name
        """, (event_id,))

        volunteers = cur.fetchall()

        return render_template('event_leader/event_volunteers.html',
                              event=event,
                              volunteers=volunteers,
                              now=now)
    except Exception as e:
        flash(f'Error loading volunteers: {e}', 'danger')
        return redirect(url_for('event_leader_manage_events'))
    finally:
        cur.close()
        conn.close()

@app.route('/event_leader/remove_volunteer/<int:event_id>/<int:user_id>', methods=['POST'])
@login_required
@role_required('event_leader')
def event_leader_remove_volunteer(event_id, user_id):
    """Remove a volunteer from an event"""
    conn = get_db_connection()
    if not conn:
        flash('Database connection error', 'danger')
        return redirect(url_for('event_leader_manage_events'))

    try:
        cur = conn.cursor()

        # Check if event belongs to this leader
        cur.execute("""
            SELECT event_id FROM events
            WHERE event_id = %s AND created_by = %s
        """, (event_id, session['user_id']))

        if not cur.fetchone():
            flash('Event not found or you do not have permission to modify it', 'danger')
            return redirect(url_for('event_leader_manage_events'))

        # Remove volunteer
        cur.execute("""
            DELETE FROM registrations
            WHERE event_id = %s AND user_id = %s
        """, (event_id, user_id))

        conn.commit()
        flash('Volunteer removed from event successfully', 'success')

    except Exception as e:
        conn.rollback()
        flash(f'Error removing volunteer: {e}', 'danger')
    finally:
        cur.close()
        conn.close()

    return redirect(url_for('event_leader_event_volunteers', event_id=event_id))

@app.route('/event_leader/track_attendance/<int:event_id>', methods=['GET', 'POST'])
@login_required
@role_required('event_leader')
def event_leader_track_attendance(event_id):
    """Track volunteer attendance for an event"""
    from datetime import datetime
    now = datetime.now()

    conn = get_db_connection()
    if not conn:
        flash('Database connection error', 'danger')
        return redirect(url_for('event_leader_manage_events'))

    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        # Get event details
        cur.execute("""
            SELECT event_id, event_name, event_date, event_time
            FROM events
            WHERE event_id = %s AND created_by = %s
        """, (event_id, session['user_id']))

        event = cur.fetchone()

        if not event:
            flash('Event not found or you do not have permission to modify it', 'danger')
            return redirect(url_for('event_leader_manage_events'))

        if request.method == 'POST':
            # Update attendance for each volunteer
            for key in request.form:
                if key.startswith('attendance_'):
                    user_id = key.replace('attendance_', '')
                    attendance_status = request.form[key]

                    cur.execute("""
                        UPDATE registrations
                        SET attendance_status = %s
                        WHERE event_id = %s AND user_id = %s
                    """, (attendance_status, event_id, user_id))

            conn.commit()
            flash('Attendance updated successfully!', 'success')
            return redirect(url_for('event_leader_event_volunteers', event_id=event_id))

        # Get volunteers registered for this event
        cur.execute("""
            SELECT u.user_id, u.username, u.full_name, r.attendance_status
            FROM users u
            JOIN registrations r ON u.user_id = r.user_id
            WHERE r.event_id = %s
            ORDER BY u.full_name
        """, (event_id,))

        volunteers = cur.fetchall()

        return render_template('event_leader/track_attendance.html',
                              event=event,
                              volunteers=volunteers,
                              now=now)
    except Exception as e:
        flash(f'Error loading attendance page: {e}', 'danger')
        return redirect(url_for('event_leader_manage_events'))
    finally:
        cur.close()
        conn.close()

@app.route('/event_leader/record_outcomes/<int:event_id>', methods=['GET', 'POST'])
@login_required
@role_required('event_leader')
def event_leader_record_outcomes(event_id):
    """Record event outcomes (bags collected, recyclables)"""
    conn = get_db_connection()
    if not conn:
        flash('Database connection error', 'danger')
        return redirect(url_for('event_leader_manage_events'))

    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        # Check if event belongs to this leader
        cur.execute("""
            SELECT event_id, event_name, event_date, bags_collected, recyclables_sorted
            FROM events
            WHERE event_id = %s AND created_by = %s
        """, (event_id, session['user_id']))

        event = cur.fetchone()

        if not event:
            flash('Event not found or you do not have permission to modify it', 'danger')
            return redirect(url_for('event_leader_manage_events'))

        if request.method == 'POST':
            bags_collected = request.form['bags_collected']
            recyclables_sorted = request.form['recyclables_sorted']

            cur.execute("""
                UPDATE events
                SET bags_collected = %s, recyclables_sorted = %s
                WHERE event_id = %s
            """, (bags_collected, recyclables_sorted, event_id))

            conn.commit()
            flash('Event outcomes recorded successfully', 'success')
            return redirect(url_for('event_leader_manage_events'))

        # Get count of registered volunteers
        cur.execute("""
            SELECT COUNT(*) as registered_count
            FROM registrations
            WHERE event_id = %s
        """, (event_id,))

        registered_count = cur.fetchone()['registered_count']

        return render_template('event_leader/record_outcomes.html',
                              event=event,
                              registered_count=registered_count)
    except Exception as e:
        flash(f'Error recording outcomes: {e}', 'danger')
        return redirect(url_for('event_leader_manage_events'))
    finally:
        cur.close()
        conn.close()

@app.route('/event_leader/participation_history')
@login_required
@role_required('event_leader')
def event_leader_participation_history():
    """View participation history for all volunteers in managed events"""
    conn = get_db_connection()
    if not conn:
        flash('Database connection error', 'danger')
        return redirect(url_for('event_leader_dashboard'))

    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        # Get all volunteers who participated in events managed by this leader
        cur.execute("""
            SELECT DISTINCT u.user_id, u.username, u.full_name, u.email,
                   (SELECT COUNT(*) FROM registrations r2
                    WHERE r2.user_id = u.user_id
                    AND r2.attendance_status = 'attended'
                    AND r2.event_id IN (SELECT event_id FROM events WHERE created_by = %s)) as events_attended,
                   (SELECT MAX(e.event_date)
                    FROM events e
                    JOIN registrations r ON e.event_id = r.event_id
                    WHERE r.user_id = u.user_id
                    AND e.created_by = %s
                    AND r.attendance_status = 'attended') as last_event_date,
                   (SELECT COUNT(*) FROM registrations r3
                    WHERE r3.user_id = u.user_id
                    AND r3.feedback_rating IS NOT NULL
                    AND r3.event_id IN (SELECT event_id FROM events WHERE created_by = %s)) as feedback_count,
                   (SELECT AVG(r4.feedback_rating)
                    FROM registrations r4
                    WHERE r4.user_id = u.user_id
                    AND r4.feedback_rating IS NOT NULL
                    AND r4.event_id IN (SELECT event_id FROM events WHERE created_by = %s)) as avg_rating
            FROM users u
            JOIN registrations r ON u.user_id = r.user_id
            JOIN events e ON r.event_id = e.event_id
            WHERE e.created_by = %s
            ORDER BY u.full_name
        """, (session['user_id'], session['user_id'], session['user_id'], session['user_id'], session['user_id']))

        volunteers = cur.fetchall()

        return render_template('event_leader/participation_history.html', volunteers=volunteers)
    except Exception as e:
        flash(f'Error loading participation history: {e}', 'danger')
        return redirect(url_for('event_leader_dashboard'))
    finally:
        cur.close()
        conn.close()

@app.route('/event_leader/volunteer_history/<int:user_id>')
@login_required
@role_required('event_leader')
def event_leader_volunteer_history(user_id):
    """View detailed participation history for a specific volunteer"""
    conn = get_db_connection()
    if not conn:
        flash('Database connection error', 'danger')
        return redirect(url_for('event_leader_participation_history'))

    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        # Get volunteer details
        cur.execute("""
            SELECT user_id, username, full_name, email, contact_number, environmental_interests
            FROM users
            WHERE user_id = %s
        """, (user_id,))
        volunteer = cur.fetchone()

        if not volunteer:
            flash('Volunteer not found', 'danger')
            return redirect(url_for('event_leader_participation_history'))

        # Get all events this volunteer participated in that are managed by this leader
        cur.execute("""
            SELECT e.event_id, e.event_name, e.location, e.event_date,
                   r.attendance_status, r.feedback_rating, r.feedback_comment, r.feedback_date
            FROM events e
            JOIN registrations r ON e.event_id = r.event_id
            WHERE r.user_id = %s AND e.created_by = %s
            ORDER BY e.event_date DESC
        """, (user_id, session['user_id']))

        events = cur.fetchall()

        # Calculate statistics
        total_events = len(events)
        attended_events = sum(1 for e in events if e['attendance_status'] == 'attended')
        feedback_count = sum(1 for e in events if e['feedback_rating'] is not None)

        if feedback_count > 0:
            avg_rating = sum(e['feedback_rating'] for e in events if e['feedback_rating']) / feedback_count
        else:
            avg_rating = 0

        return render_template('event_leader/volunteer_history.html',
                              volunteer=volunteer,
                              events=events,
                              total_events=total_events,
                              attended_events=attended_events,
                              feedback_count=feedback_count,
                              avg_rating=avg_rating)
    except Exception as e:
        flash(f'Error loading volunteer history: {e}', 'danger')
        return redirect(url_for('event_leader_participation_history'))
    finally:
        cur.close()
        conn.close()

@app.route('/event_leader/send_reminder/<int:event_id>', methods=['POST'])
@login_required
@role_required('event_leader')
def event_leader_send_reminder(event_id):
    """Send reminder to volunteers for an event"""
    conn = get_db_connection()
    if not conn:
        flash('Database connection error', 'danger')
        return redirect(url_for('event_leader_manage_events'))

    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        # Check if event belongs to this leader and is upcoming
        cur.execute("""
            SELECT event_id, event_name, event_date
            FROM events
            WHERE event_id = %s AND created_by = %s AND event_date >= CURRENT_DATE
        """, (event_id, session['user_id']))

        event = cur.fetchone()

        if not event:
            flash('Event not found, you do not have permission, or event has already passed', 'danger')
            return redirect(url_for('event_leader_manage_events'))

        # Check if there are any registered volunteers
        cur.execute("""
            SELECT COUNT(*) as count
            FROM registrations
            WHERE event_id = %s AND status = 'registered'
        """, (event_id,))

        count = cur.fetchone()['count']

        if count == 0:
            flash('No volunteers registered for this event yet', 'warning')
            return redirect(url_for('event_leader_event_volunteers', event_id=event_id))

        # Create notifications for all registered volunteers
        cur.execute("""
            INSERT INTO notifications (user_id, event_id, message, sent_date, is_read)
            SELECT user_id, %s, %s, CURRENT_TIMESTAMP, FALSE
            FROM registrations
            WHERE event_id = %s AND status = 'registered'
        """, (event_id, f'Reminder: {event["event_name"]} is coming up on {event["event_date"].strftime("%d %B %Y")}!', event_id))

        conn.commit()
        flash(f'Reminders sent successfully to {count} volunteers!', 'success')

    except Exception as e:
        conn.rollback()
        flash(f'Error sending reminders: {e}', 'danger')
    finally:
        cur.close()
        conn.close()

    return redirect(url_for('event_leader_event_volunteers', event_id=event_id))

@app.route('/event_leader/view_feedback')
@login_required
@role_required('event_leader')
def event_leader_view_feedback():
    """View feedback from volunteers for managed events"""
    conn = get_db_connection()
    if not conn:
        flash('Database connection error', 'danger')
        return redirect(url_for('event_leader_dashboard'))

    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        # Get all feedback for events managed by this leader
        cur.execute("""
            SELECT e.event_id, e.event_name, e.event_date,
                   u.user_id, u.username, u.full_name as volunteer_name,
                   r.feedback_rating, r.feedback_comment, r.feedback_date
            FROM events e
            JOIN registrations r ON e.event_id = r.event_id
            JOIN users u ON r.user_id = u.user_id
            WHERE e.created_by = %s AND r.feedback_rating IS NOT NULL
            ORDER BY r.feedback_date DESC
        """, (session['user_id'],))

        feedbacks = cur.fetchall()

        # Calculate average rating
        if feedbacks:
            avg_rating = sum(f['feedback_rating'] for f in feedbacks) / len(feedbacks)
        else:
            avg_rating = 0

        return render_template('event_leader/view_feedback.html',
                              feedbacks=feedbacks,
                              avg_rating=avg_rating,
                              total_feedback=len(feedbacks))
    except Exception as e:
        flash(f'Error loading feedback: {e}', 'danger')
        return redirect(url_for('event_leader_dashboard'))
    finally:
        cur.close()
        conn.close()

# ==================== ADMIN ROUTES ====================

@app.route('/admin/dashboard')
@login_required
@role_required('admin')
def admin_dashboard():
    """Admin dashboard"""
    conn = get_db_connection()
    if not conn:
        flash('Database connection error', 'danger')
        return redirect(url_for('index'))

    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        # Get summary statistics
        cur.execute("SELECT COUNT(*) as total_users FROM users")
        total_users = cur.fetchone()['total_users']

        cur.execute("SELECT COUNT(*) as total_volunteers FROM users WHERE role = 'volunteer'")
        total_volunteers = cur.fetchone()['total_volunteers']

        cur.execute("SELECT COUNT(*) as total_event_leaders FROM users WHERE role = 'event_leader'")
        total_event_leaders = cur.fetchone()['total_event_leaders']

        cur.execute("SELECT COUNT(*) as total_admins FROM users WHERE role = 'admin'")
        total_admins = cur.fetchone()['total_admins']

        cur.execute("SELECT COUNT(*) as total_events FROM events")
        total_events = cur.fetchone()['total_events']

        cur.execute("SELECT COUNT(*) as total_registrations FROM registrations")
        total_registrations = cur.fetchone()['total_registrations']

        # Get recent users
        cur.execute("""
            SELECT user_id, username, full_name, role, status, registration_date
            FROM users
            ORDER BY registration_date DESC
            LIMIT 5
        """)
        recent_users = cur.fetchall()

        # Get recent events
        cur.execute("""
            SELECT event_id, event_name, event_date, created_by
            FROM events
            ORDER BY created_date DESC
            LIMIT 5
        """)
        recent_events = cur.fetchall()

        return render_template('admin/dashboard.html',
                              total_users=total_users,
                              total_volunteers=total_volunteers,
                              total_event_leaders=total_event_leaders,
                              total_admins=total_admins,
                              total_events=total_events,
                              total_registrations=total_registrations,
                              recent_users=recent_users,
                              recent_events=recent_events)
    except Exception as e:
        flash(f'Error loading dashboard: {e}', 'danger')
        return redirect(url_for('index'))
    finally:
        cur.close()
        conn.close()

@app.route('/admin/users')
@login_required
@role_required('admin')
def admin_users():
    """View all users with search/filter"""
    conn = get_db_connection()
    if not conn:
        flash('Database connection error', 'danger')
        return redirect(url_for('admin_dashboard'))

    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        # Get filter parameters
        search = request.args.get('search', '')
        role_filter = request.args.get('role', '')
        status_filter = request.args.get('status', '')

        # Build query
        query = "SELECT user_id, username, full_name, email, role, status, registration_date FROM users WHERE 1=1"
        params = []

        if search:
            query += " AND (username ILIKE %s OR full_name ILIKE %s OR email ILIKE %s)"
            params.extend([f'%{search}%', f'%{search}%', f'%{search}%'])

        if role_filter:
            query += " AND role = %s"
            params.append(role_filter)

        if status_filter:
            query += " AND status = %s"
            params.append(status_filter)

        query += " ORDER BY username"

        cur.execute(query, params)
        users = cur.fetchall()

        return render_template('admin/users.html',
                              users=users,
                              current_filters={'search': search, 'role': role_filter, 'status': status_filter})
    except Exception as e:
        flash(f'Error loading users: {e}', 'danger')
        return redirect(url_for('admin_dashboard'))
    finally:
        cur.close()
        conn.close()

@app.route('/admin/user/<int:user_id>')
@login_required
@role_required('admin')
def admin_user_profile(user_id):
    """View user profile"""
    conn = get_db_connection()
    if not conn:
        flash('Database connection error', 'danger')
        return redirect(url_for('admin_users'))

    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        cur.execute("""
            SELECT user_id, username, email, full_name, home_address, contact_number,
                   environmental_interests, profile_image, role, status, registration_date
            FROM users
            WHERE user_id = %s
        """, (user_id,))

        user = cur.fetchone()

        if not user:
            flash('User not found', 'danger')
            return redirect(url_for('admin_users'))

        # Get user's event registrations
        cur.execute("""
            SELECT e.event_id, e.event_name, e.event_date, e.location,
                   r.registration_date, r.status, r.attendance_status
            FROM registrations r
            JOIN events e ON r.event_id = e.event_id
            WHERE r.user_id = %s
            ORDER BY e.event_date DESC
        """, (user_id,))

        registrations = cur.fetchall()

        return render_template('admin/user_profile.html', user=user, registrations=registrations)
    except Exception as e:
        flash(f'Error loading user profile: {e}', 'danger')
        return redirect(url_for('admin_users'))
    finally:
        cur.close()
        conn.close()

@app.route('/admin/change_user_status/<int:user_id>', methods=['POST'])
@login_required
@role_required('admin')
def admin_change_user_status(user_id):
    """Activate or deactivate a user"""
    conn = get_db_connection()
    if not conn:
        flash('Database connection error', 'danger')
        return redirect(url_for('admin_users'))

    try:
        cur = conn.cursor()

        new_status = request.form['status']

        cur.execute("""
            UPDATE users
            SET status = %s
            WHERE user_id = %s
        """, (new_status, user_id))

        conn.commit()
        flash(f'User status updated to {new_status}', 'success')

    except Exception as e:
        conn.rollback()
        flash(f'Error updating user status: {e}', 'danger')
    finally:
        cur.close()
        conn.close()

    return redirect(url_for('admin_user_profile', user_id=user_id))

@app.route('/admin/platform_reports')
@login_required
@role_required('admin')
def admin_platform_reports():
    """View platform-wide statistics"""
    conn = get_db_connection()
    if not conn:
        flash('Database connection error', 'danger')
        return redirect(url_for('admin_dashboard'))

    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        # Total counts
        cur.execute("SELECT COUNT(*) as total_events FROM events")
        total_events = cur.fetchone()['total_events']

        cur.execute("SELECT COUNT(*) as total_volunteers FROM users WHERE role = 'volunteer'")
        total_volunteers = cur.fetchone()['total_volunteers']

        cur.execute("SELECT COUNT(*) as total_event_leaders FROM users WHERE role = 'event_leader'")
        total_event_leaders = cur.fetchone()['total_event_leaders']

        cur.execute("SELECT COUNT(*) as total_admins FROM users WHERE role = 'admin'")
        total_admins = cur.fetchone()['total_admins']

        # Feedback statistics
        cur.execute("""
            SELECT
                COUNT(*) as total_feedback,
                AVG(feedback_rating) as avg_rating,
                COUNT(DISTINCT user_id) as users_with_feedback
            FROM registrations
            WHERE feedback_rating IS NOT NULL
        """)
        feedback_stats = cur.fetchone()

        # Event statistics by month
        cur.execute("""
            SELECT
                EXTRACT(YEAR FROM event_date) as year,
                EXTRACT(MONTH FROM event_date) as month,
                COUNT(*) as event_count,
                SUM(bags_collected) as total_bags,
                SUM(recyclables_sorted) as total_recyclables
            FROM events
            GROUP BY year, month
            ORDER BY year DESC, month DESC
            LIMIT 12
        """)
        monthly_stats = cur.fetchall()

        # Top volunteers
        cur.execute("""
            SELECT u.user_id, u.username, u.full_name,
                   COUNT(r.registration_id) as events_participated,
                   COUNT(r.feedback_rating) as feedback_given,
                   AVG(r.feedback_rating) as avg_rating
            FROM users u
            LEFT JOIN registrations r ON u.user_id = r.user_id
            WHERE u.role = 'volunteer'
            GROUP BY u.user_id, u.username, u.full_name
            ORDER BY events_participated DESC
            LIMIT 10
        """)
        top_volunteers = cur.fetchall()

        return render_template('admin/platform_reports.html',
                              total_events=total_events,
                              total_volunteers=total_volunteers,
                              total_event_leaders=total_event_leaders,
                              total_admins=total_admins,
                              feedback_stats=feedback_stats,
                              monthly_stats=monthly_stats,
                              top_volunteers=top_volunteers)
    except Exception as e:
        flash(f'Error loading reports: {e}', 'danger')
        return redirect(url_for('admin_dashboard'))
    finally:
        cur.close()
        conn.close()

@app.route('/admin/event_reports')
@login_required
@role_required('admin')
def admin_event_reports():
    """View event reports"""
    conn = get_db_connection()
    if not conn:
        flash('Database connection error', 'danger')
        return redirect(url_for('admin_dashboard'))

    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        # Get all events with summary data
        cur.execute("""
            SELECT e.event_id, e.event_name, e.location, e.event_date, e.event_time,
                   u.full_name as leader_name,
                   (SELECT COUNT(*) FROM registrations WHERE event_id = e.event_id) as total_registrations,
                   (SELECT COUNT(*) FROM registrations WHERE event_id = e.event_id AND attendance_status = 'attended') as attended_count,
                   e.bags_collected, e.recyclables_sorted,
                   (SELECT AVG(feedback_rating) FROM registrations WHERE event_id = e.event_id AND feedback_rating IS NOT NULL) as avg_rating
            FROM events e
            JOIN users u ON e.created_by = u.user_id
            ORDER BY e.event_date DESC
        """)

        events = cur.fetchall()

        return render_template('admin/event_reports.html', events=events)
    except Exception as e:
        flash(f'Error loading event reports: {e}', 'danger')
        return redirect(url_for('admin_dashboard'))
    finally:
        cur.close()
        conn.close()

# ==================== PROFILE ROUTES (ALL USERS) ====================

@app.route('/profile')
@login_required
def profile():
    """View user profile"""
    conn = get_db_connection()
    if not conn:
        flash('Database connection error', 'danger')
        return redirect(url_for('index'))

    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        cur.execute("""
            SELECT user_id, username, email, full_name, home_address, contact_number,
                   environmental_interests, profile_image, role, status, registration_date
            FROM users
            WHERE user_id = %s
        """, (session['user_id'],))

        user = cur.fetchone()

        return render_template('profile.html', user=user)
    except Exception as e:
        flash(f'Error loading profile: {e}', 'danger')
        return redirect(url_for('index'))
    finally:
        cur.close()
        conn.close()

@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Edit user profile"""
    conn = get_db_connection()
    if not conn:
        flash('Database connection error', 'danger')
        return redirect(url_for('profile'))

    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        if request.method == 'POST':
            full_name = request.form['full_name']
            home_address = request.form['home_address']
            contact_number = request.form['contact_number']
            environmental_interests = request.form['environmental_interests']

            # Handle profile image upload
            profile_image = None
            if 'profile_image' in request.files:
                file = request.files['profile_image']
                if file and file.filename != '' and allowed_file(file.filename):
                    filename = secure_filename(f"{session['username']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}")
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    profile_image = filename

            # Build update query
            if profile_image:
                cur.execute("""
                    UPDATE users
                    SET full_name = %s, home_address = %s, contact_number = %s,
                        environmental_interests = %s, profile_image = %s
                    WHERE user_id = %s
                """, (full_name, home_address, contact_number, environmental_interests, profile_image, session['user_id']))
            else:
                cur.execute("""
                    UPDATE users
                    SET full_name = %s, home_address = %s, contact_number = %s,
                        environmental_interests = %s
                    WHERE user_id = %s
                """, (full_name, home_address, contact_number, environmental_interests, session['user_id']))

            conn.commit()
            flash('Profile updated successfully', 'success')
            return redirect(url_for('profile'))

        # GET request - show current profile data
        cur.execute("""
            SELECT username, email, full_name, home_address, contact_number,
                   environmental_interests, profile_image
            FROM users
            WHERE user_id = %s
        """, (session['user_id'],))

        user = cur.fetchone()

        return render_template('edit_profile.html', user=user)
    except Exception as e:
        flash(f'Error editing profile: {e}', 'danger')
        return redirect(url_for('profile'))
    finally:
        cur.close()
        conn.close()

@app.route('/profile/remove_image', methods=['POST'])
@login_required
def remove_profile_image():
    """Remove profile image"""
    conn = get_db_connection()
    if not conn:
        flash('Database connection error', 'danger')
        return redirect(url_for('profile'))

    try:
        cur = conn.cursor()

        # Get current profile image
        cur.execute("SELECT profile_image FROM users WHERE user_id = %s", (session['user_id'],))
        current_image = cur.fetchone()[0]

        # Delete file if not default
        if current_image and current_image != 'default_profile.png':
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], current_image)
            if os.path.exists(file_path):
                os.remove(file_path)

        # Update database
        cur.execute("""
            UPDATE users
            SET profile_image = 'default_profile.png'
            WHERE user_id = %s
        """, (session['user_id'],))

        conn.commit()
        flash('Profile image removed', 'success')

    except Exception as e:
        conn.rollback()
        flash(f'Error removing profile image: {e}', 'danger')
    finally:
        cur.close()
        conn.close()

    return redirect(url_for('edit_profile'))

@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change user password"""
    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        # Validation
        errors = []

        if new_password != confirm_password:
            errors.append('New passwords do not match')

        if len(new_password) < 8:
            errors.append('Password must be at least 8 characters long')

        if not any(c.isupper() for c in new_password):
            errors.append('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in new_password):
            errors.append('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in new_password):
            errors.append('Password must contain at least one number')

        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('change_password.html')

        conn = get_db_connection()
        if conn:
            try:
                cur = conn.cursor()

                # Get current password hash
                cur.execute("SELECT password_hash FROM users WHERE user_id = %s", (session['user_id'],))
                current_hash = cur.fetchone()[0]

                # Verify current password
                if not bcrypt.check_password_hash(current_hash, current_password):
                    flash('Current password is incorrect', 'danger')
                    return render_template('change_password.html')

                # Check if new password is same as current
                if bcrypt.check_password_hash(current_hash, new_password):
                    flash('New password cannot be the same as current password', 'danger')
                    return render_template('change_password.html')

                # Hash new password and update
                new_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')

                cur.execute("""
                    UPDATE users
                    SET password_hash = %s
                    WHERE user_id = %s
                """, (new_hash, session['user_id']))

                conn.commit()
                flash('Password changed successfully', 'success')
                return redirect(url_for('profile'))

            except Exception as e:
                conn.rollback()
                flash(f'Error changing password: {e}', 'danger')
            finally:
                cur.close()
                conn.close()
        else:
            flash('Database connection error', 'danger')

    return render_template('change_password.html')

if __name__ == '__main__':
    app.run(debug=True)