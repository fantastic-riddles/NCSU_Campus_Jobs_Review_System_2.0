import time
from app import app, db
from app.models import Reviews, User, Job
from flask import render_template, request, redirect, url_for, session, flash
from functools import wraps



# Decorator to check if user is logged in
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash('Please log in to access this page.')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
def default():
    return redirect(url_for('home'))


@app.route('/login', methods=['GET', 'POST'])  # Route for handling the login page logic
def login():
    """
    An API for the user review page, which helps the user to add reviews.
    """
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check admin credentials
        if username == 'admin' and password == 'admin':
            session['username'] = 'admin'
            session['type'] = "admin"
            return redirect(url_for('home'))  # Redirect to admin home page

        # Query the user from the database
        user = User.query.filter_by(user_name=username).first()

        if user and password == user.password:
            session['username'] = user.user_name  # Store user ID in session
            session['type'] = user.type  # Store role in session
            return redirect(url_for('home'))  # Redirect to appropriate page
        else:
            error = 'Invalid Credentials. Please try again.'
    
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    """Logs the user out and clears the session."""
    session.clear()
    flash('You have been logged out.')
    return redirect(url_for('login'))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """
    An API for the user signup page, allowing users to create accounts as either employee or employer.
    """
    if request.method == 'POST':
        form = request.form
        email = form.get('email')
        name = form.get('full-name')
        user_name = form.get('username')
        password = form.get('password')
        type = form.get('type')  # Either 'employee' or 'employer'
        print(type)

        # Check if the username already exists
        existing_user = User.query.filter_by(user_name=user_name).first()
        if existing_user:
            error = 'Username already taken. Please choose a different one.'
            return render_template('signup.html', error=error)

        # Create a new user
        new_user = User(email=email, name=name, user_name=user_name, password=password, type=type)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('signup.html')


@app.route('/review')
@login_required
def review():
    """
    An API for the user review page, which helps the user to add reviews
    """
    entries = Reviews.query.all()
    return render_template('review-page.html', entries=entries)


@app.route('/pageContent')
@login_required
def page_content():
    """An API for the user to view all the reviews entered"""
    entries = Reviews.query.all()
    return render_template('page_content.html', entries=entries)


@app.route('/pageContentPost', methods=['POST'])
@login_required
def page_content_post():
    """An API for the user to view specific reviews depending on the job title"""
    form = request.form
    search_title = form.get('search')
    if search_title.strip() == '':
        entries = Reviews.query.all()
    else:
        entries = Reviews.query.filter_by(job_title=search_title)
    return render_template('page_content.html', entries=entries)


@app.route('/home')
@login_required
def home():
    """An API for the user to be able to access the homepage through the navbar"""
    entries = Reviews.query.all()
    return render_template('index.html', entries=entries)


@app.route('/add', methods=['POST'])
@login_required
def add():
    """An API to help users add their reviews and store it in the database"""
    form = request.form
    title = form.get('job_title')
    description = form.get('job_description')
    department = form.get('department')
    locations = form.get('locations')
    hourly_pay = form.get('hourly_pay')
    benefits = form.get('benefits')
    review = form.get('review')
    rating = form.get('rating')
    recommendation = form.get('recommendation')

    entry = Reviews(job_title=title, job_description=description, department=department, locations=locations, 
                    hourly_pay=hourly_pay, benefits=benefits, review=review, rating=rating, recommendation=recommendation)
    db.session.add(entry)
    db.session.commit()
    return redirect('/home')


@app.route('/view_users')
@login_required
def view_users():
    users = User.query.all()
    return render_template('view_users.html', users=users)

@app.route('/view-jobs')
@login_required
def view_jobs():
    jobs = Job.query.all()
    return render_template('view_jobs.html', jobs=jobs)
