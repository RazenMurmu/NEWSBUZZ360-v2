Newsbuzz360 - Flask News Portal

========================================
ABOUT
----------------------------------------
Newsbuzz360 is a modern news portal built with Flask. It supports user authentication, admin post management, categories, featured/trending articles, image uploads, and a responsive Bootstrap UI.

========================================
FEATURES
----------------------------------------
- User login/logout (admin only)
- Create, view, and delete news posts
- Categories: Technology, Entertainment, Sports, Lifestyle, News, Other
- Featured/trending articles section
- Image upload for post thumbnails
- Pagination for news feed
- Responsive design (Bootstrap 5)
- SQLite database (instance/news.db)
- Seed script for demo data

========================================
REQUIREMENTS
----------------------------------------
- Python 3.11+
- pip

Python packages (see requirements.txt.txt):
- flask
- flask_sqlalchemy
- flask_login
- flask-wtf
- wtforms
- werkzeug

========================================
INSTALLATION & RUNNING
----------------------------------------

1. Install dependencies:
   ```
   pip install -r requirements.txt.txt
   pip install flask-wtf
   ```

2. (Optional) Seed the database with demo posts:
   ```
   python seed.py
   ```

3. Run the app:
   ```
   python app.py
   ```

4. Open your browser and go to:
   ```
   http://127.0.0.1:5000/
   ```

========================================
DEFAULT ADMIN LOGIN
----------------------------------------
- Username: admin
- Password: admin123
  (You can change this by setting the ADMIN_PASSWORD environment variable before first run.)

========================================
FILE STRUCTURE
----------------------------------------
- app.py              # Main Flask app
- models.py           # SQLAlchemy models
- forms.py            # WTForms forms
- seed.py             # Demo data seeder
- requirements.txt.txt
- static/style.css    # Custom styles
- static/uploads/     # Uploaded images
- templates/          # HTML templates

========================================
NOTES
----------------------------------------
- Uploaded images are stored in static/uploads/
- To add more categories, update the choices in PostForm in forms.py.
- For production, set a secure SECRET_KEY and ADMIN_PASSWORD as environment variables.
- The app uses SQLite by default (instance/news.db).

========================================
CONTACT
----------------------------------------
For support, contact: support@example.com

========================================
Enjoy using Newsbuzz360!