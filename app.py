import os
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_caching import Cache
import bleach
from PIL import Image
from forms import LoginForm, PostForm
from models import db, User, Post, Subscriber

# ===================================================
# App Initialization & Configuration
# ===================================================
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'a-default-fallback-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///news.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024
app.config['CACHE_TYPE'] = 'SimpleCache'
app.config['CACHE_DEFAULT_TIMEOUT'] = 300

db.init_app(app)
cache = Cache(app)
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ===================================================
# Login Manager Setup
# ===================================================
login_manager = LoginManager(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ===================================================
# Template Filters & Context Processors
# ===================================================
@app.context_processor
def inject_latest_post():
    latest_post = Post.query.order_by(Post.id.desc()).first()
    return dict(latest_post=latest_post)

@app.template_filter('datetime')
def format_datetime(value, format='%B %d, %Y'):
    if isinstance(value, datetime):
        return value.strftime(format)
    return "Recent"

@app.context_processor
@cache.cached(timeout=600)
def inject_categories():
    categories = db.session.query(Post.category, db.func.count(Post.id).label('count')).filter(Post.category.isnot(None), Post.category != '').group_by(Post.category).all()
    current_year = datetime.now().year
    return dict(categories=categories, current_year=current_year)

# ===================================================
# Database Initialization
# ===================================================
def create_tables():
    with app.app_context():
        db.create_all()
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
    posts_pagination = Post.query.order_by(Post.id.desc()).paginate(page=page, per_page=5)
    featured_posts = Post.query.filter_by(featured=True).order_by(Post.id.desc()).limit(3).all()
    return render_template("index.html", featured_posts=featured_posts, posts_pagination=posts_pagination)

@app.route("/trending")
def trending():
    trending_posts = Post.query.filter_by(featured=True).order_by(Post.id.desc()).all()
    return render_template("trending.html", posts=trending_posts)

@app.route("/article/<int:id>")
def article(id):
    post = Post.query.get_or_404(id)
    related_posts = Post.query.filter(Post.category == post.category, Post.id != post.id).order_by(Post.id.desc()).limit(2).all()
    recent_posts = Post.query.order_by(Post.id.desc()).limit(5).all()
    return render_template("article.html", post=post, related_posts=related_posts, recent_posts=recent_posts)

@app.route("/category/<string:category_name>")
def category(category_name):
    posts = Post.query.filter_by(category=category_name).order_by(Post.id.desc()).all()
    return render_template("category.html", category_name=category_name, posts=posts)

@app.route("/categories")
def categories():
    return render_template("categories.html")

@app.route("/search")
def search():
    query = request.args.get('query', '')
    if not query:
        return redirect(url_for('home'))
    search_term = f"%{query}%"
    results = Post.query.filter(or_(Post.title.ilike(search_term), Post.subtitle.ilike(search_term))).order_by(Post.id.desc()).all()
    return render_template("search_results.html", posts=results, query=query)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/join-our-newsletter")
def subscribe_page():
    return render_template("subscribe_page.html")

@app.route("/subscribe", methods=["POST"])
def subscribe():
    email = request.form.get('email')
    if email:
        existing_subscriber = Subscriber.query.filter_by(email=email).first()
        if existing_subscriber:
            flash("You're already on the list! We'll notify you as soon as the feature is ready.", 'info')
        else:
            new_subscriber = Subscriber(email=email)
            db.session.add(new_subscriber)
            db.session.commit()
            flash("Thanks for your interest! This feature is coming soon, and we'll notify you once it's available.", 'success')
    else:
        flash("Please enter a valid email address.", 'danger')
    return redirect(url_for('subscribe_page'))

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

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))

# ===================================================
# Admin Routes
# ===================================================
@app.route("/b7h3-j9s2k-admin-dashboard-xyz")
@login_required
def admin():
    posts = Post.query.order_by(Post.id.desc()).all()
    return render_template("admin.html", posts=posts)

@app.route("/b7h3-j9s2k-admin-dashboard-xyz/subscribers")
@login_required
def subscribers():
    all_subscribers = Subscriber.query.order_by(Subscriber.subscribed_on.desc()).all()
    return render_template("subscribers.html", subscribers=all_subscribers)

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
                max_width = 1200
                if img.width > max_width:
                    new_height = int((max_width / img.width) * img.height)
                    img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
                img.save(filepath, optimize=True, quality=85)
            except Exception as e:
                flash(f"There was an error uploading the image: {e}")
                return redirect(url_for('create_post'))
        allowed_tags = {'p', 'b', 'i', 'u', 'strong', 'em', 'a', 'h2', 'h3', 'h4', 'img', 'blockquote'}
        allowed_attrs = {'a': ['href', 'title'], 'img': ['src', 'alt']}
        clean_content = bleach.clean(form.content.data,tags=allowed_tags, attributes=allowed_attrs)
        post = Post(title=form.title.data, subtitle=form.subtitle.data, content=clean_content, category=form.category.data.lower(), thumbnail=thumbnail_filename, featured=(form.featured.data == 'yes'))
        db.session.add(post)
        db.session.commit()
        flash("Post created successfully!")
        return redirect(url_for("admin"))
    return render_template("create_post.html", form=form)

@app.route("/edit-post/<int:id>", methods=["GET", "POST"])
@login_required
def edit_post(id):
    post = Post.query.get_or_404(id)
    form = PostForm(obj=post)
    if form.validate_on_submit():
        post.title = form.title.data
        post.subtitle = form.subtitle.data
        post.category = form.category.data.lower()
        post.featured = (form.featured.data == 'yes')
        allowed_tags = {'p', 'b', 'i', 'u', 'strong', 'em', 'a', 'h2', 'h3', 'h4', 'img', 'blockquote'}
        allowed_attrs = {'a': ['href', 'title'], 'img': ['src', 'alt']}
        post.content = bleach.clean(form.content.data, tags=allowed_tags, attributes=allowed_attrs)
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
                max_width = 1200
                if img.width > max_width:
                    new_height = int((max_width / img.width) * img.height)
                    img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
                img.save(filepath, optimize=True, quality=85)
                post.thumbnail = thumbnail_filename
            except Exception as e:
                flash(f"There was an error uploading the image: {e}")
                return redirect(url_for('edit_post', id=post.id))
        db.session.commit()
        flash("Post updated successfully!")
        return redirect(url_for("admin"))
    return render_template("edit_post.html", form=form, post=post)

@app.route("/delete/<int:id>")
@login_required
def delete(id):
    post = Post.query.get_or_404(id)
    if post.thumbnail:
        try:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], post.thumbnail))
        except FileNotFoundError:
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
    return jsonify({"uploaded": 1, "fileName": filename, "url": url})

# ===================================================
# Error Handlers
# ===================================================
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# ===================================================
# Custom CLI Commands for Admin Management
# ===================================================
@app.cli.command("create-admin")
def create_admin():
    """Creates a new admin user."""
    from getpass import getpass
    username = input("Enter admin username: ")
    password = getpass("Enter admin password: ")
    if User.query.filter_by(username=username).first():
        print(f"User '{username}' already exists.")
        return
    hashed_password = generate_password_hash(password)
    new_admin = User(username=username, password=hashed_password)
    db.session.add(new_admin)
    db.session.commit()
    print(f"Admin user '{username}' created successfully.")

@app.cli.command("update-password")
def update_password():
    """Updates an existing user's password."""
    from getpass import getpass
    username = input("Enter username of the user to update: ")
    user = User.query.filter_by(username=username).first()
    if not user:
        print(f"User '{username}' not found.")
        return
    password = getpass("Enter new password: ")
    user.password = generate_password_hash(password)
    db.session.commit()
    print(f"Password for user '{username}' updated successfully.")

# ===================================================
# Main Execution
# ===================================================
if __name__ == "__main__":
    app.run(debug=True)