import os
from werkzeug.utils import secure_filename
from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from sqlalchemy import or_
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, redirect, url_for, flash, request, jsonify

from forms import LoginForm, PostForm
from models import db, User, Post
from datetime import datetime

# ===================================================
# App Initialization & Configuration
# ===================================================
app = Flask(__name__)
# It's better to load secret keys from environment variables
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'a-default-fallback-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///news.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2MB max file size

db.init_app(app)

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ===================================================
# Login Manager Setup
# ===================================================
login_manager = LoginManager(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Add this new route to app.py

@app.route("/search")
def search():
    query = request.args.get('query', '') # Get the search query from the URL
    if not query:
        return redirect(url_for('home'))

    # Search for the query in post titles and subtitles (case-insensitive)
    search_term = f"%{query}%"
    results = Post.query.filter(
        or_(
            Post.title.ilike(search_term),
            Post.subtitle.ilike(search_term)
        )
    ).order_by(Post.id.desc()).all()

    return render_template("search_results.html", posts=results, query=query)

# ===================================================
# Template Filters & Context Processors
# ===================================================
@app.template_filter('datetime')
def format_datetime(value, format='%B %d, %Y'):
    if hasattr(value, 'created_at') and value.created_at:
        return value.created_at.strftime(format)
    elif isinstance(value, datetime):
        return value.strftime(format)
    return "Recent"

@app.context_processor
def inject_categories():
    categories = db.session.query(
        Post.category,
        db.func.count(Post.id).label('count')
    ).filter(Post.category.isnot(None)).group_by(Post.category).all()
    
    current_year = datetime.now().year
    return dict(categories=categories, current_year=current_year)

# ===================================================
# Database Initialization
# ===================================================
def create_tables():
    with app.app_context():
        db.create_all()
        # Create a default admin user if one doesn't exist
        if not User.query.filter_by(username="admin").first():
            admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')
            admin = User(username="admin", password=generate_password_hash(admin_password))
            db.session.add(admin)
            db.session.commit()

create_tables()

# ===================================================
# Main Content Routes
# ===================================================


@app.route("/")
def home():
    page = request.args.get('page', 1, type=int)
    
    # Fetch all posts using pagination (5 per page)
    posts_pagination = Post.query.order_by(Post.id.desc()).paginate(page=page, per_page=5)

    # Fetch the top 3 featured posts separately
    featured_posts = Post.query.filter_by(featured=True).order_by(Post.id.desc()).limit(3).all()
    
    return render_template("index.html", featured_posts=featured_posts, posts_pagination=posts_pagination)

@app.route("/trending")
def trending():
    # We'll define "trending" as all posts marked as featured
    trending_posts = Post.query.filter_by(featured=True).order_by(Post.id.desc()).all()
    return render_template("trending.html", posts=trending_posts)

# In app.py, replace the entire article() function with this one.

@app.route("/article/<int:id>")
def article(id):
    post = Post.query.get_or_404(id)
    
    # Fetch related posts from the same category
    related_posts = Post.query.filter(
        Post.category == post.category, 
        Post.id != post.id
    ).order_by(Post.id.desc()).limit(2).all() # Limit to 2 for the card layout

    # NEW: Fetch recent posts for the sidebar
    recent_posts = Post.query.order_by(Post.id.desc()).limit(5).all()

    return render_template(
        "article.html", 
        post=post, 
        related_posts=related_posts, 
        recent_posts=recent_posts  # Pass recent posts to the template
    )

# Add this function to your app.py file

@app.route("/category/<string:category_name>")
def category(category_name):
    # This page will show all posts belonging to a specific category
    posts = Post.query.filter_by(category=category_name).order_by(Post.id.desc()).all()
    return render_template("category.html", category_name=category_name, posts=posts)

# ===================================================
# Authentication Routes
# ===================================================
@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for("admin"))
        flash("Invalid credentials")
    return render_template("login.html", form=form)

# Add this new function to app.py

@app.route("/categories")
def categories():
    # This page will show all available categories.
    # The actual category list is already provided globally by the 'inject_categories' context processor.
    return render_template("categories.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))

# ===================================================
# Admin Routes
# ===================================================
@app.route("/admin")
@login_required
def admin():
    posts = Post.query.order_by(Post.id.desc()).all()
    return render_template("admin.html", posts=posts)

@app.route("/create-post", methods=["GET", "POST"])
@login_required
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        thumbnail_filename = None
        if form.thumbnail.data:
            file = form.thumbnail.data
            filename = secure_filename(file.filename)
            name, ext = os.path.splitext(filename)
            thumbnail_filename = f"{name}_{int(datetime.now().timestamp())}{ext}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], thumbnail_filename)

            try:
                img = Image.open(file)
                img.verify()
                img = Image.open(file)

                # --- NEW: Resize and Optimize Image ---
                max_width = 1200
                if img.width > max_width:
                    new_height = int((max_width / img.width) * img.height)
                    img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)

                img.save(filepath, optimize=True, quality=85) # Save with optimization
                # --- End of new code ---

            except Exception as e:
                flash(f"There was an error uploading the image: {e}")
                return redirect(url_for('create_post'))

        # ... (rest of the function is the same) ...
        allowed_tags = {'p', 'b', 'i', 'u', 'strong', 'em', 'a', 'h2', 'h3', 'h4', 'img', 'blockquote'}
        allowed_attrs = {'a': ['href', 'title'], 'img': ['src', 'alt', 'style']}
        clean_content = bleach.clean(
            form.content.data, 
            tags=allowed_tags, 
            attributes=allowed_attrs
        )

        post = Post(
            title=form.title.data,
            subtitle=form.subtitle.data,
            content=clean_content,
            category=form.category.data.lower(),
            thumbnail=thumbnail_filename,
            featured=(form.featured.data == 'yes')
        )
        db.session.add(post)
        db.session.commit()
        flash("Post created successfully!")
        return redirect(url_for("admin"))

    return render_template("create_post.html", form=form)

@app.route("/delete/<int:id>")
@login_required
def delete(id):
    post = Post.query.get_or_404(id)
    if post.thumbnail:
        try:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], post.thumbnail))
        except FileNotFoundError:
            # Handle case where file might already be deleted
            pass
    db.session.delete(post)
    db.session.commit()
    flash("Post deleted!")
    return redirect(url_for("admin"))

@app.route("/upload_image", methods=["POST"])
@login_required
def upload_image():
    file = request.files.get("upload")
    if not file:
        return jsonify({"uploaded": 0, "error": {"message": "No file uploaded"}})

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)

    url = url_for("static", filename="uploads/" + filename)
    return jsonify({
        "uploaded": 1,
        "fileName": filename,
        "url": url
    })

# ===================================================
# Main Execution
# ===================================================
if __name__ == "__main__":
    app.run(debug=True)