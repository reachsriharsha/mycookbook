from flask import Flask, request, session, redirect, url_for, render_template_string, flash
from functools import wraps
import hashlib

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Dummy user database
USERS = {
    'admin': {
        'password': 'admin123',
        'role': 'admin',
        'groups': ['admin', 'users']
    },
    'manager': {
        'password': 'manager123',
        'role': 'manager',
        'groups': ['managers', 'users']
    },
    'user1': {
        'password': 'user123',
        'role': 'user',
        'groups': ['users']
    }
}

def hash_password(password):
    """Simple password hashing for demo purposes"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hashed):
    """Verify password against hash"""
    return hash_password(password) == hashed

# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Role-based access decorator
def require_role(required_role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please log in to access this page.')
                return redirect(url_for('login'))
            
            user = USERS.get(session['user_id'])
            if not user or user['role'] != required_role:
                flash('You do not have permission to access this page.')
                return redirect(url_for('dashboard'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Group-based access decorator
def require_group(required_group):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please log in to access this page.')
                return redirect(url_for('login'))
            
            user = USERS.get(session['user_id'])
            if not user or required_group not in user['groups']:
                flash('You do not have permission to access this page.')
                return redirect(url_for('dashboard'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Multi-role access decorator
def require_any_role(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please log in to access this page.')
                return redirect(url_for('login'))
            
            user = USERS.get(session['user_id'])
            if not user or user['role'] not in roles:
                flash('You do not have permission to access this page.')
                return redirect(url_for('dashboard'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Specific user access decorator
def require_user(allowed_users):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please log in to access this page.')
                return redirect(url_for('login'))
            
            if session['user_id'] not in allowed_users:
                flash('You do not have permission to access this page.')
                return redirect(url_for('dashboard'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Routes
@app.route('/')
def home():
    return render_template_string('''
    <h1>Flask RBAC Demo</h1>
    <p>Welcome to the Flask Role-Based Access Control demo!</p>
    {% if session.user_id %}
        <p>Logged in as: {{ session.user_id }}</p>
        <p>Role: {{ user_role }}</p>
        <a href="{{ url_for('dashboard') }}">Go to Dashboard</a> |
        <a href="{{ url_for('logout') }}">Logout</a>
    {% else %}
        <a href="{{ url_for('login') }}">Login</a>
    {% endif %}
    ''', user_role=USERS.get(session.get('user_id'), {}).get('role', 'Unknown'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = USERS.get(username)
        if user and user['password'] == password:
            session['user_id'] = username
            flash('Login successful!')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.')
    
    return render_template_string('''
    <h2>Login</h2>
    <form method="POST">
        <p>
            <label>Username:</label><br>
            <input type="text" name="username" required>
        </p>
        <p>
            <label>Password:</label><br>
            <input type="password" name="password" required>
        </p>
        <p><input type="submit" value="Login"></p>
    </form>
    <p><small>Demo users: admin/admin123, manager/manager123, user1/user123</small></p>
    <a href="{{ url_for('home') }}">Back to Home</a>
    
    {% with messages = get_flashed_messages() %}
        {% if messages %}
            {% for message in messages %}
                <p style="color: red;">{{ message }}</p>
            {% endfor %}
        {% endif %}
    {% endwith %}
    ''')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.')
    return redirect(url_for('home'))

@app.route('/dashboard')
@login_required
def dashboard():
    user = USERS.get(session['user_id'])
    return render_template_string('''
    <h2>Dashboard</h2>
    <p>Welcome, {{ username }}!</p>
    <p>Your role: {{ user.role }}</p>
    <p>Your groups: {{ user.groups|join(', ') }}</p>
    
    <h3>Available Pages:</h3>
    <ul>
        <li><a href="{{ url_for('admin_only') }}">Admin Only Page</a></li>
        <li><a href="{{ url_for('manager_or_admin') }}">Manager/Admin Page</a></li>
        <li><a href="{{ url_for('managers_group') }}">Managers Group Page</a></li>
        <li><a href="{{ url_for('specific_users') }}">Specific Users Page</a></li>
    </ul>
    
    <a href="{{ url_for('home') }}">Home</a> | 
    <a href="{{ url_for('logout') }}">Logout</a>
    
    {% with messages = get_flashed_messages() %}
        {% if messages %}
            {% for message in messages %}
                <p style="color: green;">{{ message }}</p>
            {% endfor %}
        {% endif %}
    {% endwith %}
    ''', username=session['user_id'], user=user)

# Admin-only page
@app.route('/admin')
@require_role('admin')
def admin_only():
    return render_template_string('''
    <h2>Admin Only Page</h2>
    <p>This page is only accessible to users with admin role.</p>
    <p>Welcome, {{ session.user_id }}!</p>
    <a href="{{ url_for('dashboard') }}">Back to Dashboard</a>
    ''')

# Manager or Admin page
@app.route('/manager-admin')
@require_any_role('admin', 'manager')
def manager_or_admin():
    return render_template_string('''
    <h2>Manager/Admin Page</h2>
    <p>This page is accessible to both managers and admins.</p>
    <p>Welcome, {{ session.user_id }}!</p>
    <a href="{{ url_for('dashboard') }}">Back to Dashboard</a>
    ''')

# Group-based access (managers group)
@app.route('/managers')
@require_group('managers')
def managers_group():
    return render_template_string('''
    <h2>Managers Group Page</h2>
    <p>This page is accessible to users in the 'managers' group.</p>
    <p>Welcome, {{ session.user_id }}!</p>
    <a href="{{ url_for('dashboard') }}">Back to Dashboard</a>
    ''')

# Specific users only
@app.route('/specific-users')
@require_user(['admin', 'user1'])
def specific_users():
    return render_template_string('''
    <h2>Specific Users Page</h2>
    <p>This page is only accessible to admin and user1.</p>
    <p>Welcome, {{ session.user_id }}!</p>
    <a href="{{ url_for('dashboard') }}">Back to Dashboard</a>
    ''')

if __name__ == '__main__':
    app.run(debug=True)