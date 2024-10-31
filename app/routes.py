import time
from app import app, db
from app.email_notification import send_welcome_email
from app.models import Reviews, User, Job, Application
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
        type = form.get('type')  # Either 'applicant' or 'employer'

        # Check if the username already exists
        existing_user = User.query.filter_by(user_name=user_name).first()
        if existing_user:
            error = 'Username already taken. Please choose a different one.'
            return render_template('signup.html', error=error)

        # Create a new user
        new_user = User(email=email, name=name, user_name=user_name, password=password, type=type)
        db.session.add(new_user)
        db.session.commit()

        is_employee = True
        if type == "employer":
            is_employee = False

        send_welcome_email(email, user_name, password, is_employee)
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


@app.route('/view-jobs')
@login_required
def view_jobs():
    """
    An API for users to view jobs.
    """
    if session.get('type') == "applicant" or session.get('type') == "admin":
        jobs = Job.query.all()
        return render_template('view_jobs.html', jobs=jobs)
    return redirect(url_for('home'))



@app.route('/add-job', methods=['GET', 'POST'])
@login_required
def add_job():
    """
    An API for employers to post new jobs.
    """

    # Ensure only employers can add jobs
    if session.get('type') != 'employer':
        return redirect(url_for('home'))

    if request.method == 'POST':
        form = request.form
        title = form.get('title')
        description = form.get('description')
        location = form.get('location')
        pay = form.get('pay')

        # Get the current employer's username from the session
        employer_id = session.get('username')

        # Create a new job entry
        new_job = Job(title=title, description=description, location=location, pay=pay, employer_id=employer_id)
        db.session.add(new_job)
        db.session.commit()

        flash("Job posted successfully!")
        return redirect(url_for('home'))

    return render_template('add_job.html')


@app.route('/delete-job/<int:job_id>', methods=['POST'])
@login_required
def delete_job(job_id):
    """
    Route for admin to delete a job posting.
    Only accessible by admin users.
    """
    # Check if the current user is an admin
    if session.get('type') != 'admin':
        flash("You don't have permission to perform this action.")
        return redirect(url_for('view_jobs'))

    # Query the job by job_id
    job = Job.query.get(job_id)
    if not job:
        flash("Job not found.")
        return redirect(url_for('view_jobs'))

    # Delete the job from the database
    db.session.delete(job)
    db.session.commit()

    flash("Job deleted successfully.")
    return redirect(url_for('view_jobs'))

@app.route('/apply-job/<int:job_id>')
@login_required
def apply_job(job_id):
    """HTML page for users to apply for a job."""
    # Get the username from the session
    job = Job.query.get(job_id)
    if not job:
        flash("Job not found.")
        return redirect(url_for('view_jobs'))
    return render_template('apply_job.html',job=job)


@app.route('/apply/<int:job_id>', methods=['POST'])
@login_required
def apply(job_id):
    """An API for users to apply for a job."""
    # Get the username from the session
    user_name = session.get('username')

    # Create a new application entry
    new_application = Application(job_id=job_id, user_name=user_name)
    db.session.add(new_application)
    db.session.commit()

    flash("Application submitted successfully!")
    return redirect(url_for('view_jobs'))  # Redirect to the job listing page


@app.route('/view-applicants')
@login_required
def view_applicants():
    # Get the current user's username and type
    employer_id = session.get('username')
    user_type = session.get('type')

    # If the user is admin, fetch all applications
    if user_type == 'admin':
        applications = Application.query.all()
         # Fetch jobs posted by the employer
        jobs = Job.query.all()
    else:
        # Fetch jobs posted by the employer
        jobs = Job.query.filter_by(employer_id=employer_id).all()
        # Fetch applications for those jobs
        applications = Application.query.filter(Application.job_id.in_([job.job_id for job in jobs])).all()

    return render_template('view_applicants.html', applicants=applications, jobs=jobs)


@app.route('/delete_review/<int:review_id>', methods=['POST'])
def delete_review(review_id):
    if session.get('type') == 'admin':  # Check if the user is an admin
        review = Reviews.query.get(review_id)
        if review:
            db.session.delete(review)
            db.session.commit()
            flash('Review deleted successfully.', 'success')
        else:
            flash('Review not found.', 'danger')
    else:
        flash('You do not have permission to delete reviews.', 'danger')
    return redirect(url_for('page_content'))  # Redirect to the appropriate page


@app.route('/view-users')
def view_users():
    if session.get('type') != 'admin':
        return redirect(url_for('index'))
    
    users = User.query.all()
    return render_template('view_users.html', users=users)

@app.route('/delete_user/<string:user_name>', methods=['POST'])
def delete_user(user_name):
    if session.get('type') != 'admin':
        return redirect(url_for('index'))
    
    user = User.query.get(user_name)
    if user:
        db.session.delete(user)
        db.session.commit()
    else:
        flash(f'User {user_name} not found.')

    return redirect(url_for('view_users'))