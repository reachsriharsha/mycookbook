from flask import Flask, request, session, redirect, url_for, render_template_string, flash, jsonify
from functools import wraps
import requests
import json

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Backend API configuration
BACKEND_API_URL = 'http://localhost:8000/api'  # Your backend API URL
API_TIMEOUT = 30

class BackendAPI:
    """Helper class to interact with backend API"""
    
    @staticmethod
    def authenticate(username, password):
        """Authenticate user with backend API"""
        try:
            response = requests.post(
                f"{BACKEND_API_URL}/auth/login",
                json={'username': username, 'password': password},
                timeout=API_TIMEOUT
            )
            
            if response.status_code == 200:
                return response.json()  # Should return user data + token
            else:
                return None
        except requests.RequestException as e:
            print(f"Backend API error: {e}")
            return None
    
    @staticmethod
    def get_user_info(token):
        """Get user information from backend using token"""
        try:
            headers = {'Authorization': f'Bearer {token}'}
            response = requests.get(
                f"{BACKEND_API_URL}/auth/user",
                headers=headers,
                timeout=API_TIMEOUT
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
        except requests.RequestException as e:
            print(f"Backend API error: {e}")
            return None
    
    @staticmethod
    def refresh_token(refresh_token):
        """Refresh authentication token"""
        try:
            response = requests.post(
                f"{BACKEND_API_URL}/auth/refresh",
                json={'refresh_token': refresh_token},
                timeout=API_TIMEOUT
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
        except requests.RequestException as e:
            print(f"Backend API error: {e}")
            return None

def get_current_user():
    """Get current user information from session/backend"""
    if 'access_token' not in session:
        return None
    
    # Check if user info is cached in session
    if 'user_info' in session:
        return session['user_info']
    
    # Fetch user info from backend
    user_info = BackendAPI.get_user_info(session['access_token'])
    
    if user_info:
        session['user_info'] = user_info
        return user_info
    else:
        # Token might be expired, try to refresh
        if 'refresh_token' in session:
            token_response = BackendAPI.refresh_token(session['refresh_token'])
            if token_response:
                session['access_token'] = token_response['access_token']
                session['refresh_token'] = token_response.get('refresh_token', session['refresh_token'])
                
                # Try to get user info again
                user_info = BackendAPI.get_user_info(session['access_token'])
                if user_info:
                    session['user_info'] = user_info
                    return user_info
        
        # If all fails, clear session
        session.clear()
        return None

# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            flash('Please log in to access this page.')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Role-based access decorator
def require_role(required_role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = get_current_user()
            if not user:
                flash('Please log in to access this page.')
                return redirect(url_for('login'))
            
            if user.get('role') != required_role:
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
            user = get_current_user()
            if not user:
                flash('Please log in to access this page.')
                return redirect(url_for('login'))
            
            user_groups = user.get('groups', [])
            if required_group not in user_groups:
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
            user = get_current_user()
            if not user:
                flash('Please log in to access this page.')
                return redirect(url_for('login'))
            
            if user.get('role') not in roles:
                flash('You do not have permission to access this page.')
                return redirect(url_for('dashboard'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Permission-based access decorator
def require_permission(required_permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = get_current_user()
            if not user:
                flash('Please log in to access this page.')
                return redirect(url_for('login'))
            
            user_permissions = user.get('permissions', [])
            if required_permission not in user_permissions:
                flash('You do not have permission to access this page.')
                return redirect(url_for('dashboard'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Custom access check decorator
def require_access_check(check_function):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = get_current_user()
            if not user:
                flash('Please log in to access this page.')
                return redirect(url_for('login'))
            
            if not check_function(user):
                flash('You do not have permission to access this page.')
                return redirect(url_for('dashboard'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Routes
@app.route('/')
def home():
    user = get_current_user()
    return render_template_string('''
    <h1>Flask Frontend RBAC Demo</h1>
    <p>Welcome to the Flask Frontend with Backend API demo!</p>
    {% if user %}
        <div style="background: #f0f0f0; padding: 10px; margin: 10px 0;">
            <h3>Current User Info:</h3>
            <p><strong>Username:</strong> {{ user.username }}</p>
            <p><strong>Role:</strong> {{ user.role }}</p>
            <p><strong>Groups:</strong> {{ user.groups|join(', ') if user.groups else 'None' }}</p>
            <p><strong>Permissions:</strong> {{ user.permissions|join(', ') if user.permissions else 'None' }}</p>
        </div>
        <a href="{{ url_for('dashboard') }}">Go to Dashboard</a> |
        <a href="{{ url_for('logout') }}">Logout</a>
    {% else %}
        <a href="{{ url_for('login') }}">Login</a>
    {% endif %}
    ''', user=user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Authenticate with backend API
        auth_response = BackendAPI.authenticate(username, password)
        
        if auth_response:
            # Store tokens and user info in session
            session['access_token'] = auth_response['access_token']
            session['refresh_token'] = auth_response.get('refresh_token')
            session['user_info'] = auth_response['user']
            
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
    <p><small>Login with your backend credentials</small></p>
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
    session.clear()
    flash('You have been logged out.')
    return redirect(url_for('home'))

@app.route('/dashboard')
@login_required
def dashboard():
    user = get_current_user()
    return render_template_string('''
    <h2>Dashboard</h2>
    <p>Welcome, {{ user.username }}!</p>
    
    <div style="background: #f0f0f0; padding: 10px; margin: 10px 0;">
        <h3>Your Access Details:</h3>
        <p><strong>Role:</strong> {{ user.role }}</p>
        <p><strong>Groups:</strong> {{ user.groups|join(', ') if user.groups else 'None' }}</p>
        <p><strong>Permissions:</strong> {{ user.permissions|join(', ') if user.permissions else 'None' }}</p>
    </div>
    
    <h3>Available Pages (try clicking to test access):</h3>
    <ul>
        <li><a href="{{ url_for('admin_only') }}">Admin Only Page</a></li>
        <li><a href="{{ url_for('manager_or_admin') }}">Manager/Admin Page</a></li>
        <li><a href="{{ url_for('managers_group') }}">Managers Group Page</a></li>
        <li><a href="{{ url_for('users_with_edit_permission') }}">Users with Edit Permission</a></li>
        <li><a href="{{ url_for('custom_access_check') }}">Custom Access Check</a></li>
    </ul>
    
    <a href="{{ url_for('refresh_user_data') }}">Refresh User Data</a> |
    <a href="{{ url_for('home') }}">Home</a> | 
    <a href="{{ url_for('logout') }}">Logout</a>
    
    {% with messages = get_flashed_messages() %}
        {% if messages %}
            {% for message in messages %}
                <p style="color: green;">{{ message }}</p>
            {% endfor %}
        {% endif %}
    {% endwith %}
    ''', user=user)

@app.route('/refresh-user-data')
@login_required
def refresh_user_data():
    """Refresh user data from backend"""
    # Clear cached user info to force refresh
    session.pop('user_info', None)
    user = get_current_user()
    
    if user:
        flash('User data refreshed successfully!')
    else:
        flash('Failed to refresh user data.')
    
    return redirect(url_for('dashboard'))

# Protected pages with different access controls
@app.route('/admin')
@require_role('admin')
def admin_only():
    user = get_current_user()
    return render_template_string('''
    <h2>Admin Only Page</h2>
    <p>This page is only accessible to users with admin role.</p>
    <p>Welcome, {{ user.username }}!</p>
    <a href="{{ url_for('dashboard') }}">Back to Dashboard</a>
    ''', user=user)

@app.route('/manager-admin')
@require_any_role('admin', 'manager')
def manager_or_admin():
    user = get_current_user()
    return render_template_string('''
    <h2>Manager/Admin Page</h2>
    <p>This page is accessible to both managers and admins.</p>
    <p>Welcome, {{ user.username }}!</p>
    <a href="{{ url_for('dashboard') }}">Back to Dashboard</a>
    ''', user=user)

@app.route('/managers')
@require_group('managers')
def managers_group():
    user = get_current_user()
    return render_template_string('''
    <h2>Managers Group Page</h2>
    <p>This page is accessible to users in the 'managers' group.</p>
    <p>Welcome, {{ user.username }}!</p>
    <a href="{{ url_for('dashboard') }}">Back to Dashboard</a>
    ''', user=user)

@app.route('/edit-permission')
@require_permission('edit_content')
def users_with_edit_permission():
    user = get_current_user()
    return render_template_string('''
    <h2>Edit Permission Page</h2>
    <p>This page is accessible to users with 'edit_content' permission.</p>
    <p>Welcome, {{ user.username }}!</p>
    <a href="{{ url_for('dashboard') }}">Back to Dashboard</a>
    ''', user=user)

# Custom access check example
def custom_access_logic(user):
    """Custom logic: Allow admin or users with both 'read' and 'write' permissions"""
    if user.get('role') == 'admin':
        return True
    
    permissions = user.get('permissions', [])
    return 'read' in permissions and 'write' in permissions

@app.route('/custom-access')
@require_access_check(custom_access_logic)
def custom_access_check():
    user = get_current_user()
    return render_template_string('''
    <h2>Custom Access Check Page</h2>
    <p>This page uses custom access logic: Admin role OR users with both 'read' and 'write' permissions.</p>
    <p>Welcome, {{ user.username }}!</p>
    <a href="{{ url_for('dashboard') }}">Back to Dashboard</a>
    ''', user=user)

# API endpoint to get current user info (for AJAX calls)
@app.route('/api/current-user')
@login_required
def api_current_user():
    user = get_current_user()
    return jsonify(user)

if __name__ == '__main__':
    app.run(debug=True, port=5000)