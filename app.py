import os
import shutil
from flask import Flask, render_template_string, request, redirect, url_for, flash, session, send_file
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

# --- App Configuration ---
# Creates the Flask application instance.
app = Flask(__name__)

# Configures a secret key for session management, making it secure.
app.config['SECRET_KEY'] = os.urandom(24)

# Sets the path for the SQLite database file.
# os.path.abspath ensures the path is correct regardless of where the script is run.
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'movies.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configure upload folder for database imports
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# Initializes the SQLAlchemy extension with the Flask app.
db = SQLAlchemy(app)


# --- HTML Templates (as Python strings) ---
# This section contains all the HTML needed for the web pages.

BASE_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }} - Movie Collection</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Inter', sans-serif; }
        .form-container {
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
        }
    </style>
</head>
<body class="bg-gray-900 text-white">
    <div class="w-full max-w-5xl mx-auto p-4 sm:p-6 lg:p-8">
        <!-- Flash Messages -->
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                <div class="mb-4">
                {% for category, message in messages %}
                    <div class="p-4 text-sm rounded-lg 
                        {% if category == 'danger' %} bg-red-900 text-red-300 
                        {% elif category == 'success' %} bg-green-900 text-green-300
                        {% else %} bg-blue-900 text-blue-300 {% endif %}" role="alert">
                        {{ message }}
                    </div>
                {% endfor %}
                </div>
            {% endif %}
        {% endwith %}

        <!-- Main Content Block -->
        {{ content|safe }}
    </div>
</body>
</html>
"""

LOGIN_PAGE_CONTENT = """
<div class="flex flex-col items-center justify-center min-h-screen py-12">
    <h1 class="text-4xl font-bold text-center text-indigo-400 mb-8">Movie Collection Logger</h1>
    <div class="bg-gray-800 bg-opacity-75 p-8 rounded-2xl shadow-lg border border-gray-700 w-full max-w-md">
        <h2 class="text-2xl font-bold mb-6 text-center">Login</h2>
        <form method="POST" action="{{ url_for('login') }}" class="space-y-4">
            <input type="text" name="username" placeholder="Username" class="w-full p-3 bg-gray-700 rounded-lg border border-gray-600 focus:outline-none focus:ring-2 focus:ring-indigo-500" required>
            <input type="password" name="password" placeholder="Password" class="w-full p-3 bg-gray-700 rounded-lg border border-gray-600 focus:outline-none focus:ring-2 focus:ring-indigo-500" required>
            <button type="submit" class="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-3 rounded-lg transition duration-300">Login</button>
        </form>
        <p class="text-center mt-6">
            Don't have an account? <a href="{{ url_for('register') }}" class="text-indigo-400 hover:underline">Sign Up</a>
        </p>
    </div>
</div>
"""

REGISTER_PAGE_CONTENT = """
<div class="flex flex-col items-center justify-center min-h-screen py-12">
    <h1 class="text-4xl font-bold text-center text-indigo-400 mb-8">Movie Collection Logger</h1>
    <div class="bg-gray-800 bg-opacity-75 p-8 rounded-2xl shadow-lg border border-gray-700 w-full max-w-md">
        <h2 class="text-2xl font-bold mb-6 text-center">Sign Up</h2>
        <form method="POST" action="{{ url_for('register') }}" class="space-y-4">
            <input type="text" name="username" placeholder="Username" class="w-full p-3 bg-gray-700 rounded-lg border border-gray-600 focus:outline-none focus:ring-2 focus:ring-indigo-500" required>
            <input type="password" name="password" placeholder="Password" class="w-full p-3 bg-gray-700 rounded-lg border border-gray-600 focus:outline-none focus:ring-2 focus:ring-indigo-500" required>
            <button type="submit" class="w-full bg-green-600 hover:bg-green-700 text-white font-bold py-3 rounded-lg transition duration-300">Sign Up</button>
        </form>
        <p class="text-center mt-6">
            Already have an account? <a href="{{ url_for('login') }}" class="text-indigo-400 hover:underline">Login</a>
        </p>
    </div>
</div>
"""

INDEX_PAGE_CONTENT = """
<div>
    <div class="flex flex-wrap justify-between items-center mb-8 gap-4">
        <h1 class="text-3xl font-bold text-indigo-400">My Movie Collection</h1>
        <div class="flex items-center gap-4">
            {% if user.is_admin %}
            <a href="{{ url_for('admin_dashboard') }}" class="bg-yellow-600 hover:bg-yellow-700 text-white font-bold py-2 px-4 rounded-lg transition duration-300">Admin Dashboard</a>
            {% endif %}
            <a href="{{ url_for('logout') }}" class="bg-red-600 hover:bg-red-700 text-white font-bold py-2 px-4 rounded-lg transition duration-300">Logout</a>
        </div>
    </div>
    
    <!-- Add Movie Form -->
    <div class="bg-gray-800 p-6 rounded-2xl shadow-lg mb-8 border border-gray-700">
        <h2 class="text-2xl font-semibold mb-4">Add a New Movie</h2>
        <form method="POST" action="{{ url_for('add_movie') }}" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 items-end">
            <div class="lg:col-span-1">
                <label for="movie-name" class="block text-sm font-medium text-gray-400 mb-1">Movie Name</label>
                <input type="text" id="movie-name" name="movie-name" placeholder="e.g., The Matrix" class="w-full p-3 bg-gray-700 rounded-lg border border-gray-600 focus:outline-none focus:ring-2 focus:ring-indigo-500" required>
            </div>
            <div>
                <label for="movie-format" class="block text-sm font-medium text-gray-400 mb-1">Format</label>
                <select id="movie-format" name="movie-format" class="w-full p-3 bg-gray-700 rounded-lg border border-gray-600 focus:outline-none focus:ring-2 focus:ring-indigo-500 h-[50px]">
                    <option>Blu-ray</option>
                    <option>DVD</option>
                    <option>4K UHD</option>
                    <option>Digital</option>
                    <option>VHS</option>
                    <option>Other</option>
                </select>
            </div>
            <div>
                <label for="movie-barcode" class="block text-sm font-medium text-gray-400 mb-1">Barcode (UPC)</label>
                <input type="text" id="movie-barcode" name="movie-barcode" placeholder="e.g., 085391171421" class="w-full p-3 bg-gray-700 rounded-lg border border-gray-600 focus:outline-none focus:ring-2 focus:ring-indigo-500">
            </div>
             <div>
                <label for="media-condition" class="block text-sm font-medium text-gray-400 mb-1">Media Condition</label>
                <select id="media-condition" name="media-condition" class="w-full p-3 bg-gray-700 rounded-lg border border-gray-600 focus:outline-none focus:ring-2 focus:ring-indigo-500 h-[50px]">
                    <option>New (Sealed)</option>
                    <option>Like New</option>
                    <option>Very Good</option>
                    <option>Good</option>
                    <option>Acceptable</option>
                </select>
            </div>
            <div class="lg:col-start-3">
                <button type="submit" class="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-3 rounded-lg transition duration-300 h-[50px]">Add Movie</button>
            </div>
        </form>
    </div>
    
    <!-- Search and Filter Form -->
    <div class="bg-gray-800 p-6 rounded-2xl shadow-lg mb-8 border border-gray-700">
        <form method="GET" action="{{ url_for('index') }}" class="grid grid-cols-1 md:grid-cols-3 gap-4 items-center">
            <div class="md:col-span-1">
                <input type="text" name="search" placeholder="Search by title..." value="{{ request.args.get('search', '') }}" class="w-full p-3 bg-gray-700 rounded-lg border border-gray-600 focus:outline-none focus:ring-2 focus:ring-indigo-500">
            </div>
            <div>
                <select name="sort" class="w-full p-3 bg-gray-700 rounded-lg border border-gray-600 focus:outline-none focus:ring-2 focus:ring-indigo-500 h-[50px]">
                    <option value="name_asc" {% if request.args.get('sort') == 'name_asc' %}selected{% endif %}>Sort by Title (A-Z)</option>
                    <option value="name_desc" {% if request.args.get('sort') == 'name_desc' %}selected{% endif %}>Sort by Title (Z-A)</option>
                    <option value="date_added_desc" {% if request.args.get('sort') == 'date_added_desc' %}selected{% endif %}>Sort by Date Added (Newest)</option>
                    <option value="date_added_asc" {% if request.args.get('sort') == 'date_added_asc' %}selected{% endif %}>Sort by Date Added (Oldest)</option>
                </select>
            </div>
            <div>
                <select name="filter_format" class="w-full p-3 bg-gray-700 rounded-lg border border-gray-600 focus:outline-none focus:ring-2 focus:ring-indigo-500 h-[50px]">
                    <option value="">Filter by Format (All)</option>
                    <option value="Blu-ray" {% if request.args.get('filter_format') == 'Blu-ray' %}selected{% endif %}>Blu-ray</option>
                    <option value="DVD" {% if request.args.get('filter_format') == 'DVD' %}selected{% endif %}>DVD</option>
                    <option value="4K UHD" {% if request.args.get('filter_format') == '4K UHD' %}selected{% endif %}>4K UHD</option>
                    <option value="Digital" {% if request.args.get('filter_format') == 'Digital' %}selected{% endif %}>Digital</option>
                    <option value="VHS" {% if request.args.get('filter_format') == 'VHS' %}selected{% endif %}>VHS</option>
                    <option value="Other" {% if request.args.get('filter_format') == 'Other' %}selected{% endif %}>Other</option>
                </select>
            </div>
            <div class="md:col-span-3 text-center">
                 <button type="submit" class="w-full md:w-auto bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-3 px-6 rounded-lg transition duration-300">Apply</button>
            </div>
        </form>
    </div>


    <!-- Movie List -->
    <div class="bg-gray-800 p-6 rounded-2xl shadow-lg border border-gray-700">
        <h2 class="text-2xl font-semibold mb-4">Your Movies</h2>
        <div class="space-y-4">
        {% if movies %}
            {% for movie in movies %}
            <div class="flex items-center justify-between bg-gray-700 p-4 rounded-lg">
                <div class="flex-grow">
                    <p class="font-bold text-lg">{{ movie.name }}</p>
                    <p class="text-sm text-gray-400">
                        Format: <span class="font-semibold text-indigo-300">{{ movie.format }}</span> | 
                        Condition: <span class="font-semibold text-indigo-300">{{ movie.condition }}</span>
                        {% if movie.barcode %}| UPC: <span class="font-semibold text-indigo-300">{{ movie.barcode }}</span>{% endif %}
                    </p>
                </div>
                <form method="POST" action="{{ url_for('delete_movie', movie_id=movie.id) }}" class="ml-4">
                    <button type="submit" class="bg-red-600 hover:bg-red-800 text-white font-bold py-2 px-3 rounded-lg transition duration-300" onclick="return confirm('Are you sure you want to remove this movie?');">
                        &times;
                    </button>
                </form>
            </div>
            {% endfor %}
        {% else %}
            <p class="text-gray-400 text-center py-4">No movies found. Try adjusting your search or add your first movie!</p>
        {% endif %}
        </div>
    </div>
</div>
"""

ADMIN_PAGE_CONTENT = """
<div>
    <div class="flex justify-between items-center mb-8">
        <h1 class="text-3xl font-bold text-yellow-400">Admin Dashboard</h1>
        <a href="{{ url_for('index') }}" class="bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-2 px-4 rounded-lg transition duration-300">Back to Collection</a>
    </div>

    <div class="bg-gray-800 p-6 rounded-2xl shadow-lg border border-gray-700 mb-8">
        <h2 class="text-2xl font-semibold mb-4">Database Management</h2>
        <div class="flex flex-col sm:flex-row gap-4">
            <a href="{{ url_for('admin_export_db') }}" class="w-full sm:w-auto text-center bg-green-600 hover:bg-green-700 text-white font-bold py-3 px-6 rounded-lg transition duration-300">Export Database Backup</a>
            <form method="POST" action="{{ url_for('admin_import_db') }}" enctype="multipart/form-data" class="w-full sm:w-auto">
                <input type="file" name="db_file" class="w-full text-sm text-gray-400 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-blue-600 file:text-white hover:file:bg-blue-700" required>
                <button type="submit" class="w-full mt-2 sm:mt-0 sm:w-auto bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded-lg transition duration-300" onclick="return confirm('Are you sure? This will overwrite the current database.');">Import Database</button>
            </form>
        </div>
    </div>

    <div class="bg-gray-800 p-6 rounded-2xl shadow-lg border border-gray-700">
        <h2 class="text-2xl font-semibold mb-4">User Management</h2>
        <div class="space-y-4">
        {% if users %}
            {% for user in users %}
            <div class="flex flex-col sm:flex-row items-center justify-between bg-gray-700 p-4 rounded-lg gap-4">
                <p class="font-semibold text-lg">{{ user.username }}</p>
                <form method="POST" action="{{ url_for('admin_reset_password', user_id=user.id) }}" class="flex items-center gap-2 w-full sm:w-auto">
                    <input type="password" name="new_password" placeholder="New Password" class="w-full sm:w-auto p-2 bg-gray-600 rounded-lg border border-gray-500 focus:outline-none focus:ring-2 focus:ring-yellow-500" required>
                    <button type="submit" class="bg-yellow-600 hover:bg-yellow-700 text-white font-bold py-2 px-4 rounded-lg transition duration-300">Reset</button>
                </form>
            </div>
            {% endfor %}
        {% else %}
            <p class="text-gray-400 text-center py-4">There are no other users to manage.</p>
        {% endif %}
        </div>
    </div>
</div>
"""

# --- Database Models ---
class User(db.Model):
    """User model for storing user accounts."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    movies = db.relationship('Movie', backref='owner', lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Movie(db.Model):
    """Movie model for storing movie collection data."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    format = db.Column(db.String(50), nullable=False)
    barcode = db.Column(db.String(50), nullable=True)
    condition = db.Column(db.String(50), nullable=False)
    date_added = db.Column(db.DateTime, server_default=db.func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


# --- Routes ---
@app.route('/')
def index():
    """Main page: shows movies if logged in, otherwise redirects to login."""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = db.session.get(User, session['user_id'])
    
    # Base query for the logged-in user's movies
    query = Movie.query.filter_by(user_id=user.id)
    
    # Search
    search_term = request.args.get('search')
    if search_term:
        query = query.filter(Movie.name.ilike(f'%{search_term}%'))
        
    # Filter
    filter_format = request.args.get('filter_format')
    if filter_format:
        query = query.filter_by(format=filter_format)
        
    # Sort
    sort_by = request.args.get('sort', 'name_asc')
    if sort_by == 'name_asc':
        query = query.order_by(Movie.name.asc())
    elif sort_by == 'name_desc':
        query = query.order_by(Movie.name.desc())
    elif sort_by == 'date_added_desc':
        query = query.order_by(Movie.date_added.desc())
    elif sort_by == 'date_added_asc':
        query = query.order_by(Movie.date_added.asc())
    
    movies = query.all()
    
    full_template = BASE_TEMPLATE.replace('{{ content|safe }}', INDEX_PAGE_CONTENT)
    return render_template_string(full_template, title="My Collection", movies=movies, user=user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handles user login."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            session['user_id'] = user.id
            flash('Logged in successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password.', 'danger')
    
    full_template = BASE_TEMPLATE.replace('{{ content|safe }}', LOGIN_PAGE_CONTENT)
    return render_template_string(full_template, title="Login")

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Handles new user registration. The first user becomes an admin."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if User.query.filter_by(username=username).first():
            flash('Username already taken.', 'warning')
            return redirect(url_for('register'))

        is_first_user = User.query.count() == 0
        new_user = User(username=username, is_admin=is_first_user)
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    full_template = BASE_TEMPLATE.replace('{{ content|safe }}', REGISTER_PAGE_CONTENT)
    return render_template_string(full_template, title="Sign Up")

@app.route('/logout')
def logout():
    """Logs the user out."""
    session.pop('user_id', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/add_movie', methods=['POST'])
def add_movie():
    """Adds a new movie to the current user's collection."""
    if 'user_id' not in session:
        return redirect(url_for('login'))

    new_movie = Movie(
        name=request.form.get('movie-name'),
        format=request.form.get('movie-format'),
        barcode=request.form.get('movie-barcode'),
        condition=request.form.get('media-condition'),
        user_id=session['user_id']
    )
    db.session.add(new_movie)
    db.session.commit()
    flash('Movie added to your collection!', 'success')
    return redirect(url_for('index'))

@app.route('/delete_movie/<int:movie_id>', methods=['POST'])
def delete_movie(movie_id):
    """Deletes a movie from the collection."""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    movie_to_delete = db.session.get(Movie, movie_id)
    
    if movie_to_delete and movie_to_delete.user_id == session['user_id']:
        db.session.delete(movie_to_delete)
        db.session.commit()
        flash('Movie removed from your collection.', 'success')
    else:
        flash('Movie not found or you do not have permission to delete it.', 'danger')

    return redirect(url_for('index'))

# --- Admin Routes ---
@app.route('/admin')
def admin_dashboard():
    """Displays the admin dashboard."""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    current_user = db.session.get(User, session['user_id'])
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('index'))
    
    users_to_manage = User.query.filter(User.id != current_user.id).all()
    
    full_template = BASE_TEMPLATE.replace('{{ content|safe }}', ADMIN_PAGE_CONTENT)
    return render_template_string(full_template, title="Admin Dashboard", users=users_to_manage)

@app.route('/admin/reset_password/<int:user_id>', methods=['POST'])
def admin_reset_password(user_id):
    """Handles password reset by an admin."""
    if 'user_id' not in session or not db.session.get(User, session['user_id']).is_admin:
        flash('You do not have permission to perform this action.', 'danger')
        return redirect(url_for('index'))
        
    user_to_update = db.session.get(User, user_id)
    new_password = request.form.get('new_password')
    
    if user_to_update and new_password:
        user_to_update.set_password(new_password)
        db.session.commit()
        flash(f"Password for {user_to_update.username} has been reset.", 'success')
    else:
        flash("Failed to reset password.", 'danger')
        
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/export')
def admin_export_db():
    """Allows admin to download a copy of the database."""
    if 'user_id' not in session or not db.session.get(User, session['user_id']).is_admin:
        flash('You do not have permission to perform this action.', 'danger')
        return redirect(url_for('index'))
    
    try:
        return send_file(db_path, as_attachment=True, download_name='movies_backup.db')
    except Exception as e:
        flash(f"Error exporting database: {e}", 'danger')
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/import', methods=['POST'])
def admin_import_db():
    """Allows admin to upload and replace the database."""
    if 'user_id' not in session or not db.session.get(User, session['user_id']).is_admin:
        flash('You do not have permission to perform this action.', 'danger')
        return redirect(url_for('index'))
        
    if 'db_file' not in request.files:
        flash('No file part in the request.', 'danger')
        return redirect(url_for('admin_dashboard'))
        
    file = request.files['db_file']
    if file.filename == '':
        flash('No selected file.', 'danger')
        return redirect(url_for('admin_dashboard'))
        
    if file and file.filename.endswith('.db'):
        # It's critical to stop using the current DB before replacing it.
        # In a real production app, you'd need a more robust process.
        db.session.close_all()

        # Save the uploaded file securely
        filename = secure_filename(file.filename)
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(temp_path)
        
        # Replace the old database with the new one
        shutil.move(temp_path, db_path)
        
        flash('Database imported successfully. The application is using the new database.', 'success')
        # A restart might be needed in some server configurations, but Flask's reloader handles it in debug mode.
    else:
        flash('Invalid file type. Please upload a .db file.', 'danger')

    return redirect(url_for('admin_dashboard'))


# --- Main Execution ---
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5002, debug=True)
