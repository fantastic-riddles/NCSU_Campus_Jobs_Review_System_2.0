"""
This module contains the routing logic for a job portal web application, built using Flask. 

The main routes and functionalities include:
- **User Authentication**: Routes for login, logout, and signup, allowing users to authenticate, register, and manage sessions.
- **Job Listings**: Routes for employers to add, view, and delete job listings and for applicants to view and apply for jobs.
- **Reviews**: Routes for users to submit, view, and delete reviews about jobs.
- **Application Management**: Allows applicants to apply to jobs and employers (or admins) to view applications for specific jobs.
- **User Management**: Admins can view and delete user accounts, with session management to restrict access based on user roles.
- **Static Pages**: Access to About Us and Contact Us pages, available through the navigation bar.

Key Components:
- `login_required`: A decorator to enforce user authentication before accessing specific routes.
- `send_welcome_email`: A utility for sending welcome emails to users upon registration.
- HTML templates render views for all routes, displaying job listings, user reviews, applications, and other static content.

Routes:
- Authentication (`/login`, `/logout`, `/signup`)
- Job-related actions (`/view-jobs`, `/add-job`, `/delete-job/<job_id>`, `/apply-job/<job_id>`)
- Review actions (`/review`, `/pageContent`, `/delete_review/<review_id>`)
- User management (`/view-users`, `/delete_user/<user_name>`)
- Static pages (`/about`, `/contact`)

Each route interacts with the database, managing user sessions, and displays specific templates.
"""
from app.inappropriate_words import badwords
from functools import wraps
from flask import render_template, request, redirect, url_for, session, flash
from app import app, db
from app.email_notification import send_welcome_email, send_new_job_email
from app.models import Reviews, User, Job, Application,Upvote, Experience


# Decorator to check if user is logged in
def login_required(f):
    """This function checks whether the user has logged in or not"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        """
        This is a wrapper function to check whether user is in session or not
        """
        if 'username' not in session:
            flash('Please log in to access this page.')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
def default():
    """
    This API directs directly to homepage
    """
    return redirect(url_for('home'))

@app.route('/upvote/<int:review_id>', methods=['POST'])
@login_required
def upvote_review(review_id):
    """Allow a user to upvote a review"""
    user_name = session.get('username')

    # Check if the user has already upvoted this review
    existing_upvote = Upvote.query.filter_by(review_id=review_id, user_name=user_name).first()
    
    if existing_upvote:
        flash('You have already upvoted this review.')
        return redirect(url_for('page_content'))

    # Add an upvote entry
    new_upvote = Upvote(review_id=review_id, user_name=user_name)
    db.session.add(new_upvote)

    # Increment the review's upvote count
    review = Reviews.query.get(review_id)
    if review:
        review.upvote_count += 1
        db.session.commit()
        flash('Upvoted successfully!')
    
    return redirect(url_for('page_content'))

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

        if user and password == user.password: # pylint: disable=no-member
            session['username'] = user.user_name  # Store user ID in session
            session['type'] = user.type  # Store role in session
            return redirect(url_for('home'))  # Redirect to appropriate page
        else:
            error = 'Invalid Credentials. Please try again.' # pylint: disable=no-member

    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    """Logs the user out and clears the session."""
    session.clear()
    return redirect(url_for('login'))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """
    An API for user signup page, allowing users to create accounts as either employee or employer.
    """
    if request.method == 'POST':
        form = request.form
        email = form.get('email')
        name = form.get('full-name')
        user_name = form.get('username')
        password = form.get('password')
        role = form.get('type')  # Either 'applicant' or 'employer'

        # Check if the username already exists
        existing_user = User.query.filter_by(user_name=user_name).first()
        if existing_user:
            error = 'Username already taken. Please choose a different one.'
            return render_template('signup.html', error=error)

        # Create a new user
        new_user = User(email=email, name=name, user_name=user_name, password=password, type=role)
        db.session.add(new_user) # pylint: disable=no-member
        db.session.commit() # pylint: disable=no-member

        is_employee = True
        if role == "employer":
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
    if session.get('type') == 'employer':
        return redirect(url_for('home'))
    entries = Reviews.query.all()
    return render_template('review-page.html', entries=entries)


@app.route('/pageContent')
@login_required
def page_content():
    """An API for the user to view all the reviews entered"""
    if session.get('type') == 'employer':
        return redirect(url_for('home'))
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
    review_sample = form.get('review')
    rating = form.get('rating')
    recommendation = form.get('recommendation')
    inappropriate_words_list=badwords()
    filtered_review = ' '.join(
    word for word in review_sample.split()
    if word.lower() not in inappropriate_words_list
)   
    entry = Reviews(job_title=title, job_description=description,
                    department=department, locations=locations,
                    hourly_pay=hourly_pay, benefits=benefits,
                    review=filtered_review, rating=rating,
                    recommendation=recommendation)
    db.session.add(entry) # pylint: disable=no-member
    db.session.commit() # pylint: disable=no-member
    return redirect('/home')


@app.route('/view-jobs')
@login_required
def view_jobs():
    """
    An API for users to view jobs.
    """
    if session.get('type') == "applicant" or session.get('type') == "admin":
        jobs = Job.query.all()
        applications = Application.query.filter_by(user_name= session.get('username')).all()
        applied_job_ids_array = list(map(get_job_ids, applications))
        return render_template('view_jobs.html', jobs=jobs,applications=applications,applied_job_ids_array=applied_job_ids_array)
    return redirect(url_for('home'))

def get_job_ids(application):
    """
    This function is used to get all the job ids in the application table.
    """
    return application.job_id

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
        db.session.add(new_job) # pylint: disable=no-member
        db.session.commit() # pylint: disable=no-member

        # Fetch all email addresses from the 'users' table
        emails = [user.email for user in User.query.with_entities(User.email).all()]

        flash("Job posted successfully!")
        for email in emails:
            send_new_job_email(email, title, description, location, pay)
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
    db.session.delete(job) # pylint: disable=no-member
    db.session.commit() # pylint: disable=no-member

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
    db.session.add(new_application) # pylint: disable=no-member
    db.session.commit() # pylint: disable=no-member

    flash("Application submitted successfully!")
    return redirect(url_for('view_jobs'))  # Redirect to the job listing page


@app.route('/view-applicants')
@login_required
def view_applicants():
    """
    This function displays all the applications
    """
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
    """
    This function gets admin rights to delete the reviews if he wants.
    """
    if session.get('type') == 'admin':  # Check if the user is an admin
        review_rows = Reviews.query.get(review_id)
        if review_rows:
            db.session.delete(review_rows) # pylint: disable=no-member
            db.session.commit() # pylint: disable=no-member
            flash('Review deleted successfully.', 'success')
        else:
            flash('Review not found.', 'danger')
    else:
        flash('You do not have permission to delete reviews.', 'danger')
    return redirect(url_for('page_content'))  # Redirect to the appropriate page


@app.route('/view-users')
def view_users():
    """
    This function is used to view the users in the system
    """
    if session.get('type') != 'admin':
        return redirect(url_for('home'))

    users = User.query.all()
    return render_template('view_users.html', users=users)

@app.route('/delete_user/<string:user_name>', methods=['POST'])
def delete_user(user_name):
    """
    This function deletes the username from the system/database
    """
    if session.get('type') != 'admin':
        return redirect(url_for('home'))

    user = User.query.get(user_name)
    if user:
        db.session.delete(user) # pylint: disable=no-member
        db.session.commit() # pylint: disable=no-member
    else:
        flash(f'User {user_name} not found.')

    return redirect(url_for('view_users'))

@app.route('/about')
@login_required
def about_us():
    """An API for the user to be able to access the About Us through the navbar"""
    entries = Reviews.query.all()
    return render_template('about.html', entries=entries)

@app.route('/contact')
@login_required
def contact_us():
    """An API for the user to be able to access the Contact Us through the navbar"""
    entries = Reviews.query.all()
    return render_template('contact.html', entries=entries)

@app.route('/add-experience', methods=['GET', 'POST'])
@login_required
def add_experience():
    if request.method == 'POST':
        linkedin_url = request.form.get('linkedin_url')  # Getting LinkedIn URL from form
        cover_letter = request.form.get('cover_letter')
        prev_experience = request.form.get('prev_experience')

        # Get the current user's username from the session
        user_name = session.get('username')

        # Check if the user already has an experience
        existing_experience = Experience.query.filter_by(user_name=user_name).first()
        if existing_experience:
            flash('Experience already exists. Please update it instead.')
            return redirect(url_for('update_experience'))  # Redirect to update experience

        # Create a new experience entry
        new_experience = Experience(
            user_name=user_name,
            linkedin_url=linkedin_url,  # Using linkedin_url instead of years_of_experience
            cover_letter=cover_letter,
            prev_experience=prev_experience
        )
        db.session.add(new_experience)
        db.session.commit()
        flash('Experience added successfully!')
        return redirect(url_for('profile'))  # Redirect to the user's profile page

    return render_template('add_experience.html')  # Render the form template


@app.route('/update-experience', methods=['GET', 'POST'])
@login_required
def update_experience():
    # Get the current user's username from the session
    user_name = session.get('username')
    experience = Experience.query.filter_by(user_name=user_name).first()

    if not experience:
        flash('No experience found. Please add your experience first.')
        return redirect(url_for('add_experience'))  # Redirect to add experience page if not found

    if request.method == 'POST':
        experience.linkedin_url = request.form.get('linkedin_url')  # Updating linkedin_url
        experience.cover_letter = request.form.get('cover_letter')
        experience.prev_experience = request.form.get('prev_experience')

        db.session.commit()
        flash('Experience updated successfully!')
        return redirect(url_for('profile'))  # Redirect to the user's profile page

    return render_template('update_experience.html', experience=experience)  # Render a form with existing data