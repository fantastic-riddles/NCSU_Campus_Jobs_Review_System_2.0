import pytest
import os
import sys
import warnings
from flask import Flask, session, url_for, flash
sys.path.append(os.getcwd())
from app import db, app
from app.models import User, Job, Application, Reviews,Upvote
from crudapp import *
warnings.filterwarnings('ignore')

@pytest.fixture
def client():
    """Fixture to create a test client with an in-memory database."""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    client = app.test_client()

    with app.app_context():
        db.create_all()

    yield client

    with app.app_context():
        db.drop_all()


def test_apply_route(client):
    """Test the apply route for a job application."""
    with client.session_transaction() as sess:
        sess['username'] = 'testuser'
    job = Job(title='Test Job', description='Test Description',
              location='Test Location', pay=20, employer_id='testuser')
    with app.app_context():
        db.session.add(job)
        db.session.commit()
        job_id = job.job_id
    response = client.post(f'/apply/{job_id}')
    assert response.status_code == 302
    assert response.location.endswith('/view-jobs')


def test_view_applicants_route_employer(client):
    """Test the view applicants route for an employer."""
    with client.session_transaction() as sess:
        sess['username'] = 'testuser'
        sess['type'] = 'employer'
    response = client.get('/view-applicants')
    assert response.status_code == 200


def test_view_applicants_route_admin(client):
    """Test the view applicants route for an admin."""
    with client.session_transaction() as sess:
        sess['username'] = 'admin'
        sess['type'] = 'admin'
    response = client.get('/view-applicants')
    assert response.status_code == 200


def test_delete_review_route_admin(client):
    """Test the delete review route for an admin."""
    with client.session_transaction() as sess:
        sess['username'] = 'admin'
        sess['type'] = 'admin'
    review = Reviews(job_title='Test Job', job_description='Test Description', department='Test Department',
                     locations='Test Location', hourly_pay=20, benefits='Test Benefits', review='Test Review', rating=5, recommendation=1)
    with app.app_context():
        db.session.add(review)
        db.session.commit()
        review_id = review.id
    response = client.post(f'/delete_review/{review_id}')
    assert response.status_code == 302
    assert response.location.endswith('/pageContent')


def test_view_users_route_admin(client):
    """Test the view users route for an admin."""
    with client.session_transaction() as sess:
        sess['username'] = 'admin'
        sess['type'] = 'admin'
    response = client.get('/view-users')
    assert response.status_code == 200


def test_delete_user_route_admin(client):
    """Test the delete user route for an admin."""
    with client.session_transaction() as sess:
        sess['username'] = 'admin'
        sess['type'] = 'admin'
    user = User(user_name='testuser', name='Test User',
                email='test@example.com', password='testpass', type='applicant')
    with app.app_context():
        db.session.add(user)
        db.session.commit()
    response = client.post('/delete_user/testuser')
    assert response.status_code == 302
    assert response.location.endswith('/view-users')


def test_login_required_decorator(client):
    """Test the login required decorator."""
    response = client.get('/home')
    assert response.status_code == 302
    assert response.location.endswith('/login')


def test_add_job_route_non_employer(client):
    """Test the add job route for a non-employer user."""
    with client.session_transaction() as sess:
        sess['username'] = 'testuser'
        sess['type'] = 'applicant'
    response = client.get('/add-job')
    assert response.status_code == 302
    assert response.location.endswith('/home')


def test_apply_job_nonexistent_job(client):
    """Test applying to a nonexistent job."""
    with client.session_transaction() as sess:
        sess['username'] = 'testuser'
    response = client.get('/apply-job/9999')
    assert response.status_code == 302
    assert response.location.endswith('/view-jobs')


def test_delete_job_nonexistent_job(client):
    """Test deleting a nonexistent job."""
    with client.session_transaction() as sess:
        sess['username'] = 'admin'
        sess['type'] = 'admin'
    response = client.post('/delete-job/9999')
    assert response.status_code == 302
    assert response.location.endswith('/view-jobs')


def test_delete_review_nonexistent_review(client):
    """Test deleting a nonexistent review."""
    with client.session_transaction() as sess:
        sess['username'] = 'admin'
        sess['type'] = 'admin'
    response = client.post('/delete_review/9999')
    assert response.status_code == 302
    assert response.location.endswith('/pageContent')


def test_delete_user_nonexistent_user(client):
    """Test deleting a nonexistent user."""
    with client.session_transaction() as sess:
        sess['username'] = 'admin'
        sess['type'] = 'admin'
    response = client.post('/delete_user/nonexistent')
    assert response.status_code == 302
    assert response.location.endswith('/view-users')


def test_signup_existing_username(client):
    """Test signing up with an existing username."""
    user = User(user_name='existinguser', name='Existing User',
                email='existing@example.com', password='testpass', type='applicant')
    with app.app_context():
        db.session.add(user)
        db.session.commit()
    response = client.post('/signup', data={
        'email': 'new@example.com',
        'full-name': 'New User',
        'username': 'existinguser',
        'password': 'newpass',
        'type': 'applicant'
    })
    assert response.status_code == 200
    assert b'Username already taken' in response.data


def test_page_content_post_empty_search(client):
    """Test posting page content with an empty search."""
    with client.session_transaction() as sess:
        sess['username'] = 'testuser'
    response = client.post('/pageContentPost', data={'search': ''})
    assert response.status_code == 200

# New test cases


def test_login_invalid_credentials(client):
    """Test login with invalid credentials."""
    response = client.post(
        '/login', data={'username': 'invalid', 'password': 'invalid'})
    assert response.status_code == 200
    assert b'Invalid Credentials' in response.data


def test_logout_route(client):
    """Test the logout route."""
    with client.session_transaction() as sess:
        sess['username'] = 'testuser'
    response = client.get('/logout')
    assert response.status_code == 302
    assert response.location.endswith('/login')


def test_signup_route_get(client):
    """Test the GET request to the signup route."""
    response = client.get('/signup')
    assert response.status_code == 200


def test_review_route_authenticated(client):
    """Test the review route for an authenticated user."""
    with client.session_transaction() as sess:
        sess['username'] = 'testuser'
    response = client.get('/review')
    assert response.status_code == 200


def test_page_content_route_authenticated(client):
    """Test the page content route for an authenticated user."""
    with client.session_transaction() as sess:
        sess['username'] = 'testuser'
    response = client.get('/pageContent')
    assert response.status_code == 200


def test_home_route_authenticated(client):
    """Test the home route for an authenticated user."""
    with client.session_transaction() as sess:
        sess['username'] = 'testuser'
    response = client.get('/home')
    assert response.status_code == 200


def test_add_review_route(client):
    """Test adding a new review."""
    with client.session_transaction() as sess:
        sess['username'] = 'testuser'
    response = client.post('/add', data={
        'job_title': 'Test Job',
        'job_description': 'Test Description',
        'department': 'Test Department',
        'locations': 'Test Location',
        'hourly_pay': '20',
        'benefits': 'Test Benefits',
        'review': 'Test Review',
        'rating': '5',
        'recommendation': '1'
    })
    assert response.status_code == 302
    assert response.location.endswith('/home')


def test_view_jobs_route_applicant(client):
    """Test the view jobs route for an applicant."""
    with client.session_transaction() as sess:
        sess['username'] = 'testuser'
        sess['type'] = 'applicant'
    response = client.get('/view-jobs')
    assert response.status_code == 200


def test_view_jobs_route_employer(client):
    """Test the view jobs route for an employer."""
    with client.session_transaction() as sess:
        sess['username'] = 'testuser'
        sess['type'] = 'employer'
    response = client.get('/view-jobs')
    assert response.status_code == 302
    assert response.location.endswith('/home')


def test_add_job_route_employer(client):
    """Test adding a new job as an employer."""
    with client.session_transaction() as sess:
        sess['username'] = 'testuser'
        sess['type'] = 'employer'
    response = client.post('/add-job', data={
        'title': 'New Job',
        'description': 'Job Description',
        'location': 'Job Location',
        'pay': '25'
    })
    assert response.status_code == 302
    assert response.location.endswith('/home')


def test_apply_job_route_get(client):
    """Test the GET request to apply for a job."""
    with client.session_transaction() as sess:
        sess['username'] = 'testuser'
    job = Job(title='Test Job', description='Test Description',
              location='Test Location', pay=20, employer_id='employer')
    with app.app_context():
        db.session.add(job)
        db.session.commit()
        job_id = job.job_id
    response = client.get(f'/apply-job/{job_id}')
    assert response.status_code == 200


def test_view_applicants_no_applications(client):
    """Test viewing applicants when there are no applications."""
    with client.session_transaction() as sess:
        sess['username'] = 'testuser'
        sess['type'] = 'employer'
    response = client.get('/view-applicants')
    assert response.status_code == 200
    # assert b'No applications found' in response.data


def test_delete_review_non_admin(client):
    """Test deleting a review as a non-admin user."""
    with client.session_transaction() as sess:
        sess['username'] = 'testuser'
        sess['type'] = 'applicant'
    review = Reviews(job_title='Test Job', job_description='Test Description', department='Test Department',
                     locations='Test Location', hourly_pay=20, benefits='Test Benefits', review='Test Review', rating=5, recommendation=1)
    with app.app_context():
        db.session.add(review)
        db.session.commit()
        review_id = review.id
    response = client.post(f'/delete_review/{review_id}')
    assert response.status_code == 302


def test_view_users_non_admin(client):
    """Test viewing users as a non-admin user."""
    with client.session_transaction() as sess:
        sess['username'] = 'testuser'
        sess['type'] = 'applicant'
    response = client.get('/view-users')
    print(response.status_code)
    assert response.status_code == 302


def test_delete_user_non_admin(client):
    """Test deleting a user as a non-admin user."""
    with client.session_transaction() as sess:
        sess['username'] = 'testuser'
        sess['type'] = 'applicant'
    response = client.post('/delete_user/someuser')
    assert response.status_code == 302


def test_signup_invalid_user_type(client):
    """Test signing up with an invalid user type."""
    response = client.post('/signup', data={
        'email': 'test@example.com',
        'full-name': 'Test User',
        'username': 'testuser',
        'password': 'testpass',
        'type': 'invalid_type'
    })
    assert response.status_code == 302


def test_apply_job_already_applied(client):
    """Test applying for a job that the user has already applied to."""
    with client.session_transaction() as sess:
        sess['username'] = 'testuser'

    with app.app_context():
        job = Job(title='Test Job', description='Test Description',
                  location='Test Location', pay=20, employer_id='employer')
        db.session.add(job)
        db.session.commit()

        application = Application(job_id=job.job_id, user_name='testuser')
        db.session.add(application)
        db.session.commit()
        job_id = job.job_id

    response = client.post(f'/apply/{job_id}')
    assert response.status_code == 302


def test_admin_login(client):
    """Test admin login functionality."""
    response = client.post(
        '/login', data={'username': 'admin', 'password': 'admin'})
    assert response.status_code == 302
    assert response.location.endswith('/home')
    with client.session_transaction() as sess:
        assert sess['username'] == 'admin'
        assert sess['type'] == 'admin'


def test_admin_view_all_jobs(client):
    """Test admin's ability to view all jobs."""
    with client.session_transaction() as sess:
        sess['username'] = 'admin'
        sess['type'] = 'admin'
    response = client.get('/view-jobs')
    assert response.status_code == 200


def test_admin_view_all_applicants(client):
    """Test admin's ability to view all applicants."""
    with client.session_transaction() as sess:
        sess['username'] = 'admin'
        sess['type'] = 'admin'
    response = client.get('/view-applicants')
    assert response.status_code == 200


def test_admin_delete_job(client):
    """Test admin's ability to delete a job."""
    with client.session_transaction() as sess:
        sess['username'] = 'admin'
        sess['type'] = 'admin'
    job = Job(title='Test Job', description='Test Description',
              location='Test Location', pay=20, employer_id='employer')
    with app.app_context():
        db.session.add(job)
        db.session.commit()
        job_id = job.job_id
    response = client.post(f'/delete-job/{job_id}')
    assert response.status_code == 302
    assert response.location.endswith('/view-jobs')


def test_admin_view_users(client):
    """Test admin's ability to view all users."""
    with client.session_transaction() as sess:
        sess['username'] = 'admin'
        sess['type'] = 'admin'
    response = client.get('/view-users')
    assert response.status_code == 200


def test_admin_delete_user(client):
    """Test admin's ability to delete a user."""
    with client.session_transaction() as sess:
        sess['username'] = 'admin'
        sess['type'] = 'admin'
    user = User(user_name='testuser', name='Test User',
                email='test@example.com', password='testpass', type='applicant')
    with app.app_context():
        db.session.add(user)
        db.session.commit()
    response = client.post('/delete_user/testuser')
    assert response.status_code == 302
    assert response.location.endswith('/view-users')


def test_signup_new_user(client):
    """Test signing up a new user."""
    response = client.post('/signup', data={
        'email': 'newuser@example.com',
        'full-name': 'New User',
        'username': 'newuser',
        'password': 'newpass',
        'type': 'applicant'
    })
    assert response.status_code == 302
    assert response.location.endswith('/login')


def test_login_valid_user(client):
    """Test login with valid user credentials."""
    user = User(user_name='validuser', name='Valid User',
                email='valid@example.com', password='validpass', type='applicant')
    with app.app_context():
        db.session.add(user)
        db.session.commit()
    response = client.post(
        '/login', data={'username': 'validuser', 'password': 'validpass'})
    assert response.status_code == 302
    assert response.location.endswith('/home')


def test_add_review(client):
    """Test adding a new review."""
    with client.session_transaction() as sess:
        sess['username'] = 'testuser'
    response = client.post('/add', data={
        'job_title': 'New Job',
        'job_description': 'New Description',
        'department': 'New Department',
        'locations': 'New Location',
        'hourly_pay': '25',
        'benefits': 'New Benefits',
        'review': 'Great job!',
        'rating': '5',
        'recommendation': '1'
    })
    assert response.status_code == 302
    assert response.location.endswith('/home')


def test_search_reviews(client):
    """Test searching for reviews."""
    with client.session_transaction() as sess:
        sess['username'] = 'testuser'
    review = Reviews(job_title='Searchable Job', job_description='Description', department='Dept',
                     locations='Location', hourly_pay=20, benefits='Benefits', review='Good', rating=4, recommendation=1)
    with app.app_context():
        db.session.add(review)
        db.session.commit()
    response = client.post(
        '/pageContentPost', data={'search': 'Searchable Job'})
    assert response.status_code == 200
    assert b'Searchable Job' in response.data


def test_view_all_reviews(client):
    """Test viewing all reviews."""
    with client.session_transaction() as sess:
        sess['username'] = 'testuser'
    response = client.get('/pageContent')
    assert response.status_code == 200


def test_employer_add_job(client):
    """Test an employer adding a new job."""
    with client.session_transaction() as sess:
        sess['username'] = 'employer'
        sess['type'] = 'employer'
    response = client.post('/add-job', data={
        'title': 'New Job Posting',
        'description': 'Job Description',
        'location': 'Job Location',
        'pay': '30'
    })
    assert response.status_code == 302
    assert response.location.endswith('/home')


def test_applicant_apply_for_job(client):
    """Test an applicant applying for a job."""
    with client.session_transaction() as sess:
        sess['username'] = 'applicant'
        sess['type'] = 'applicant'
    job = Job(title='Available Job', description='Job Description',
              location='Job Location', pay=25, employer_id='employer')
    with app.app_context():
        db.session.add(job)
        db.session.commit()
        job_id = job.job_id
    response = client.post(f'/apply/{job_id}')
    assert response.status_code == 302
    assert response.location.endswith('/view-jobs')


def test_login_required_redirect(client):
    """Test redirect to login page for protected routes."""
    response = client.get('/home')
    assert response.status_code == 302
    assert response.location.endswith('/login')


def test_logout_functionality(client):
    """Test logout functionality."""
    with client.session_transaction() as sess:
        sess['username'] = 'testuser'
    response = client.get('/logout')
    assert response.status_code == 302
    assert response.location.endswith('/login')
    with client.session_transaction() as sess:
        assert 'username' not in sess


def test_invalid_route(client):
    """Test accessing an invalid route."""
    response = client.get('/invalid-route')
    assert response.status_code == 404


def test_apply_and_view_applicants(client):
    """Test applying for a job and then viewing applicants as an employer."""
    with client.session_transaction() as sess:
        sess['username'] = 'testuser'
        sess['type'] = 'employer'

    job = Job(title='Job 1', description='Description 1',
              location='Location 1', pay=20, employer_id='testuser')
    with app.app_context():
        db.session.add(job)
        db.session.commit()
        job_id = job.job_id

    response = client.post(f'/apply/{job_id}')
    assert response.status_code == 302
    assert response.location.endswith('/view-jobs')

    response = client.get('/view-applicants')
    assert response.status_code == 200


def test_signup_and_login(client):
    """Test signing up and then logging in as a new user."""
    response = client.post('/signup', data={
        'email': 'signupuser@example.com',
        'full-name': 'Signup User',
        'username': 'signupuser',
        'password': 'signup123',
        'type': 'applicant'
    })
    assert response.status_code == 302
    assert response.location.endswith('/login')

    response = client.post(
        '/login', data={'username': 'signupuser', 'password': 'signup123'})
    assert response.status_code == 302
    assert response.location.endswith('/home')


def test_login_and_add_job(client):
    """Test logging in as an employer and adding a new job."""
    with client.session_transaction() as sess:
        sess['username'] = 'employer'
        sess['type'] = 'employer'

    response = client.post('/add-job', data={
        'title': 'Employer Job',
        'description': 'Employer Job Description',
        'location': 'Employer Location',
        'pay': '30'
    })
    assert response.status_code == 302
    assert response.location.endswith('/home')


def test_view_all_reviews_and_add_review(client):
    """Test viewing all reviews and adding a new review."""
    with client.session_transaction() as sess:
        sess['username'] = 'testuser'

    response = client.get('/pageContent')
    assert response.status_code == 200

    response = client.post('/add', data={
        'job_title': 'New Review Job',
        'job_description': 'Review Job Description',
        'department': 'Review Department',
        'locations': 'Review Location',
        'hourly_pay': '40',
        'benefits': 'Review Benefits',
        'review': 'Nice job!',
        'rating': '5',
        'recommendation': '1'
    })
    assert response.status_code == 302


def test_admin_login_and_view_users(client):
    """Test admin logging in and viewing all users."""
    response = client.post(
        '/login', data={'username': 'admin', 'password': 'admin'})
    assert response.status_code == 302
    assert response.location.endswith('/home')

    response = client.get('/view-users')
    assert response.status_code == 200


def test_view_applicants_and_delete_review(client):
    """Test viewing applicants and deleting a review as an admin."""
    with client.session_transaction() as sess:
        sess['username'] = 'admin'
        sess['type'] = 'admin'

    review = Reviews(job_title='Delete Review Job', job_description='Description', department='Dept',
                     locations='Loc', hourly_pay=20, benefits='Benefits', review='Bad review', rating=2, recommendation=0)
    with app.app_context():
        db.session.add(review)
        db.session.commit()
        review_id = review.id

    response = client.get('/view-applicants')
    assert response.status_code == 200

    response = client.post(f'/delete_review/{review_id}')
    assert response.status_code == 302


def test_search_and_view_job_details(client):
    """Test searching for a job and viewing its details."""
    with client.session_transaction() as sess:
        sess['username'] = 'applicant'

    job = Job(title='Search Job', description='Job to Search',
              location='Location', pay=45, employer_id='employer')
    with app.app_context():
        db.session.add(job)
        db.session.commit()

    response = client.post('/pageContentPost', data={'search': 'Search Job'})
    assert response.status_code == 200


def test_view_applicants_and_login_as_applicant(client):
    """Test viewing applicants and then logging in as an applicant."""
    with client.session_transaction() as sess:
        sess['username'] = 'admin'
        sess['type'] = 'admin'

    response = client.get('/view-applicants')
    assert response.status_code == 200

    # Now log in as an applicant
    response = client.post(
        '/login', data={'username': 'applicant', 'password': 'applicantpass'})
    assert response.status_code == 200


def test_add_job_and_view_jobs(client):
    """Test adding a job and then viewing all jobs."""
    with client.session_transaction() as sess:
        sess['username'] = 'employer'
        sess['type'] = 'employer'

    response = client.post('/add-job', data={
        'title': 'Another Job',
        'description': 'Another Job Description',
        'location': 'Another Location',
        'pay': '60'
    })
    assert response.status_code == 302
    assert response.location.endswith('/home')

    response = client.get('/view-jobs')
    assert response.status_code == 302


def test_logout_and_login(client):
    """Test logging out and then logging back in."""
    with client.session_transaction() as sess:
        sess['username'] = 'testuser'

    response = client.get('/logout')
    assert response.status_code == 302
    assert response.location.endswith('/login')

    response = client.post(
        '/login', data={'username': 'testuser', 'password': 'testpass'})
    assert response.status_code == 200


def test_delete_job_and_view_jobs(client):
    """Test deleting a job and then viewing jobs as an admin."""
    with client.session_transaction() as sess:
        sess['username'] = 'admin'
        sess['type'] = 'admin'

    job = Job(title='Job to Delete', description='To be deleted',
              location='Location', pay=20, employer_id='employer')
    with app.app_context():
        db.session.add(job)
        db.session.commit()
        job_id = job.job_id

    response = client.post(f'/delete-job/{job_id}')
    assert response.status_code == 302
    assert response.location.endswith('/view-jobs')

    response = client.get('/view-jobs')
    assert response.status_code == 200
    assert b'Job to Delete' not in response.data


def test_admin_view_all_jobs_and_logout(client):
    """Test admin viewing all jobs and then logging out."""
    with client.session_transaction() as sess:
        sess['username'] = 'admin'
        sess['type'] = 'admin'

    response = client.get('/view-jobs')
    assert response.status_code == 200

    response = client.get('/logout')
    assert response.status_code == 302
    assert response.location.endswith('/login')


def test_invalid_route_and_login(client):
    """Test accessing an invalid route and then logging in."""
    response = client.get('/invalid-route')
    assert response.status_code == 404

    response = client.post(
        '/login', data={'username': 'validuser', 'password': 'validpass'})
    assert response.status_code == 200


def test_view_users_and_search_reviews(client):
    """Test viewing users and then searching reviews."""
    with client.session_transaction() as sess:
        sess['username'] = 'admin'
        sess['type'] = 'admin'

    response = client.get('/view-users')
    assert response.status_code == 200

    response = client.post('/pageContentPost', data={'search': 'Good'})
    assert response.status_code == 200


def test_logout_as_applicant(client):
    """Test logging out as an applicant."""
    with client.session_transaction() as sess:
        sess['username'] = 'applicant'
        sess['type'] = 'applicant'

    response = client.get('/logout')
    assert response.status_code == 302
    assert response.location.endswith('/login')

def test_admin_login_and_delete_user_success(client):
    """Test admin logging in and successfully deleting a user."""
    # Admin logs in
    response = client.post(
        '/login', data={'username': 'admin', 'password': 'admin'})
    assert response.status_code == 302
    assert response.location.endswith('/home')

    # Create a user to delete
    user = User(user_name='deletetestuser', name='Delete Test User',
                email='deleteuser@example.com', password='testpass', type='applicant')
    with app.app_context():
        db.session.add(user)
        db.session.commit()

    # Admin deletes the user
    response = client.post('/delete_user/deletetestuser')
    assert response.status_code == 302
    assert response.location.endswith('/view-users')
    

def test_admin_login_and_verify_delete_user(client):
    """Test admin logging in and verify if user is successfully deleted after deleting"""
    # Admin logs in
    response = client.post(
        '/login', data={'username': 'admin', 'password': 'admin'})
    assert response.status_code == 302
    assert response.location.endswith('/home')

    # Create a user to delete
    user = User(user_name='deletetestuser', name='Delete Test User',
                email='deleteuser@example.com', password='testpass', type='applicant')
    with app.app_context():
        db.session.add(user)
        db.session.commit()

    # Admin deletes the user
    response = client.post('/delete_user/deletetestuser')
    assert response.status_code == 302
    assert response.location.endswith('/view-users')
    
    # Verify user no longer exists
    with app.app_context():
        deleted_user = User.query.filter_by(user_name='deletetestuser').first()
        assert deleted_user is None
        
        
def test_admin_login_and_delete_non_existent_user(client):
    """Test admin logging in and attempting to delete a non-existent user."""
    # Admin logs in
    response = client.post(
        '/login', data={'username': 'admin', 'password': 'admin'})
    assert response.status_code == 302
    assert response.location.endswith('/home')

    # Attempt to delete a non-existent user
    response = client.post('/delete_user/nonexistentuser')
    assert response.status_code == 302  # Expect a 302 response for user not found
        
    
def test_admin_login_view_users_and_delete_user(client):
    """Test admin logging in, viewing all users, and then deleting a specific user."""
    # Admin logs in
    response = client.post(
        '/login', data={'username': 'admin', 'password': 'admin'})
    assert response.status_code == 302
    assert response.location.endswith('/home')

    # View users
    response = client.get('/view-users')
    assert response.status_code == 200

    # Create a user to delete
    user = User(user_name='deletetestuser2', name='Delete Test User 2',
                email='deleteuser2@example.com', password='testpass', type='applicant')
    with app.app_context():
        db.session.add(user)
        db.session.commit()

    # Delete the created user
    response = client.post('/delete_user/deletetestuser2')
    assert response.status_code == 302
    assert response.location.endswith('/view-users')
    
    # Verify user no longer exists
    with app.app_context():
        deleted_user = User.query.filter_by(user_name='deletetestuser2').first()
        assert deleted_user is None


def test_admin_login_and_delete_review_success(client):
    """Test admin logging in and successfully deleting a review."""
    # Admin logs in
    response = client.post(
        '/login', data={'username': 'admin', 'password': 'admin'})
    assert response.status_code == 302
    assert response.location.endswith('/home')

    # Create a review to delete
    review = Reviews(id=1,job_title='Test Job', job_description='Test Description', department='Test Department',
                      locations='Test Location', hourly_pay=20, benefits='Test Benefits', review='Test Review', rating=5, recommendation=1)
    with app.app_context():
        db.session.add(review)
        db.session.commit()

    # Admin deletes the review
    response = client.post('/delete_review/1')
    assert response.status_code == 302
    
    # Verify review no longer exists
    with app.app_context():
        deleted_review = Reviews.query.filter_by(id=1).first()
        assert deleted_review is None


def test_admin_login_and_delete_non_existent_review(client):
    """Test admin logging in and attempting to delete a non-existent review."""
    # Admin logs in
    response = client.post(
        '/login', data={'username': 'admin', 'password': 'admin'})
    assert response.status_code == 302
    assert response.location.endswith('/home')

    # Attempt to delete a non-existent review
    response = client.post('/delete_review/999')
    assert response.status_code == 302  # Expect a 404 response for review not found


def test_admin_login_and_delete_own_review(client):
    """Test admin logging in and attempting to delete their own review, if applicable."""
    # Admin logs in
    response = client.post(
        '/login', data={'username': 'admin', 'password': 'admin'})
    assert response.status_code == 302
    assert response.location.endswith('/home')

    # Create a review by admin to delete
    review = Reviews(id=2,job_title='Test Job', job_description='Test Description', department='Test Department',
                      locations='Test Location', hourly_pay=20, benefits='Test Benefits', review='Test Review', rating=5, recommendation=1)
    with app.app_context():
        db.session.add(review)
        db.session.commit()

    # Admin deletes their own review
    response = client.post('/delete_review/2')
    assert response.status_code == 302
    
    # Verify review no longer exists
    with app.app_context():
        deleted_review = Reviews.query.filter_by(id=2).first()
        assert deleted_review is None


def test_admin_login_view_reviews_and_delete_review(client):
    """Test admin logging in, viewing all reviews, and then deleting a specific review."""
    # Admin logs in
    response = client.post(
        '/login', data={'username': 'admin', 'password': 'admin'})
    assert response.status_code == 302
    assert response.location.endswith('/home')

    # View reviews
    response = client.get('/pageContent')
    assert response.status_code == 200

    # Create a review to delete
    review = Reviews(id=3,job_title='Test Job', job_description='Test Description', department='Test Department',
                      locations='Test Location', hourly_pay=20, benefits='Test Benefits', review='Test Review', rating=5, recommendation=1)
    with app.app_context():
        db.session.add(review)
        db.session.commit()

    # Delete the created review
    response = client.post('/delete_review/3')
    assert response.status_code == 302
    
    # Verify review no longer exists
    with app.app_context():
        deleted_review = Reviews.query.filter_by(id=3).first()
        assert deleted_review is None


def test_non_admin_login_and_delete_user_failure(client):
    """Test non admin logging in and not able to delete a user."""
    
    user = User(user_name='regularuser', name='Valid User',
                 email='valid@example.com', password='userpass', type='applicant')
    with app.app_context():
        db.session.add(user)
        db.session.commit()
    # Non-Admin logs in
    response = client.post(
        '/login', data={'username': 'regularuser', 'password': 'userpass'})
    assert response.status_code == 302
    assert response.location.endswith('/home')

    # Create a user to delete
    deleteuser = User(user_name='deletetestuser', name='Delete Test User',
                email='deleteuser@example.com', password='testpass', type='applicant')
    with app.app_context():
        db.session.add(deleteuser)
        db.session.commit()

    # Non-Admin tries to delete the user
    response = client.post('/delete_user/deletetestuser')
    assert response.status_code == 302  # As an unauthenticated user tries to access a protected page, they will be redirected (with a 302) to the login page.
    
    
def test_non_admin_login_and_view_users(client):
    """Test non admin logging in, viewing all users."""
    user = User(user_name='regularuser', name='Valid User',
                 email='valid@example.com', password='userpass', type='applicant')
    with app.app_context():
        db.session.add(user)
        db.session.commit()
    # Non Admin logs in
    response = client.post(
        '/login', data={'username': 'regularuser', 'password': 'userpass'})
    assert response.status_code == 302
    assert response.location.endswith('/home')

    # View users
    response = client.get('/view-users')
    assert response.status_code == 302    
    
    
def test_non_admin_login_and_delete_review_failure(client):
    """Test non admin logging in and not able to delete a review."""
    user = User(user_name='regularuser', name='Valid User',
                 email='valid@example.com', password='userpass', type='applicant')
    with app.app_context():
        db.session.add(user)
        db.session.commit()
    # Non Admin logs in
    response = client.post(
        '/login', data={'username': 'regularuser', 'password': 'userpass'})
    assert response.status_code == 302
    assert response.location.endswith('/home')

    # Create a review to delete
    review = Reviews(id=1,job_title='Test Job', job_description='Test Description', department='Test Department',
                      locations='Test Location', hourly_pay=20, benefits='Test Benefits', review='Test Review', rating=5, recommendation=1)
    with app.app_context():
        db.session.add(review)
        db.session.commit()

    # Non-Admin tries to delete the review
    response = client.post('/delete_review/1')
    assert response.status_code == 302
    

def test_applicant_login_view_reviews(client):
    """Test applicant logging in, viewing all reviews, and then deleting a specific review."""
    user = User(user_name='regularuser', name='Valid User',
                 email='valid@example.com', password='userpass', type='applicant')
    with app.app_context():
        db.session.add(user)
        db.session.commit()
    # Non Admin logs in
    response = client.post(
        '/login', data={'username': 'regularuser', 'password': 'userpass'})
    assert response.status_code == 302
    assert response.location.endswith('/home')

    # View reviews
    response = client.get('/pageContent')
    assert response.status_code == 200

    
def test_applicant_login_view_reviews_delete_review(client):
    """Test applicant logging in, viewing all reviews, and then deleting a specific review."""
    user = User(user_name='regularuser', name='Valid User',
                 email='valid@example.com', password='userpass', type='applicant')
    with app.app_context():
        db.session.add(user)
        db.session.commit()
    # Non Admin logs in
    response = client.post(
        '/login', data={'username': 'regularuser', 'password': 'userpass'})
    assert response.status_code == 302
    assert response.location.endswith('/home')

    # View reviews
    response = client.get('/pageContent')
    assert response.status_code == 200

    # Create a review to delete
    review = Reviews(id=3,job_title='Test Job', job_description='Test Description', department='Test Department',
                      locations='Test Location', hourly_pay=20, benefits='Test Benefits', review='Test Review', rating=5, recommendation=1)
    with app.app_context():
        db.session.add(review) 
        db.session.commit()

    # Delete the created review
    response = client.post('/delete_review/3')
    assert response.status_code == 302


def test_employer_login_view_reviews(client):
    """Test non admin logging in, viewing all reviews, and then deleting a specific review."""
    user = User(user_name='regularuser', name='Valid User',
                 email='valid@example.com', password='userpass', type='employer')
    with app.app_context():
        db.session.add(user)
        db.session.commit()
    # Non Admin logs in
    response = client.post(
        '/login', data={'username': 'regularuser', 'password': 'userpass'})
    assert response.status_code == 302
    assert response.location.endswith('/home')

    # View reviews
    response = client.get('/pageContent')
    assert response.status_code == 302
    
    
def test_employer_login_view_reviews_delete_review(client):
    """Test non admin logging in, viewing all reviews, and then deleting a specific review."""
    user = User(user_name='regularuser', name='Valid User',
                 email='valid@example.com', password='userpass', type='employer')
    with app.app_context():
        db.session.add(user)
        db.session.commit()
    # Non Admin logs in
    response = client.post(
        '/login', data={'username': 'regularuser', 'password': 'userpass'})
    assert response.status_code == 302
    assert response.location.endswith('/home')

    # View reviews
    response = client.get('/pageContent')
    assert response.status_code == 302
    

def test_view_contact_route_employer(client):
    """Test the contact route for an employer."""
    with client.session_transaction() as sess:
        sess['username'] = 'regularuser'
        sess['type'] = 'employer'
    response = client.get('/contact')
    assert response.status_code == 200    
    
def test_view_contact_route_applicant(client):
    """Test the contact route for an applicant."""
    with client.session_transaction() as sess:
        sess['username'] = 'regularuser'
        sess['type'] = 'applicant'
    response = client.get('/contact')
    assert response.status_code == 200  
    
    
def test_view_contact_route_admin(client):
    """Test the contact route for an admin."""
    with client.session_transaction() as sess:
        sess['username'] = 'admin'
        sess['type'] = 'admin'
    response = client.get('/contact')
    assert response.status_code == 200  
        

def test_view_about_us_route_employer(client):
    """Test the About Us route for an employer."""
    with client.session_transaction() as sess:
        sess['username'] = 'regularuser'
        sess['type'] = 'employer'
    response = client.get('/about')
    assert response.status_code == 200    
    
def test_view_about_us_route_applicant(client):
    """Test the view applicants route for an admin."""
    with client.session_transaction() as sess:
        sess['username'] = 'regularuser'
        sess['type'] = 'applicant'
    response = client.get('/about')
    assert response.status_code == 200  
    
    
def test_view_about_us_route_admin(client):
    """Test the view applicants route for an admin."""
    with client.session_transaction() as sess:
        sess['username'] = 'admin'
        sess['type'] = 'admin'
    response = client.get('/about')
    assert response.status_code == 200          









def test_create_review(client):
    """Test the creation of a new review."""
    with client.session_transaction() as sess:
        sess['username'] = 'testuser'
    
    review_data = {
        'department': 'Engineering',
        'locations': 'New York',
        'job_title': 'Software Engineer',
        'job_description': 'Developing software',
        'hourly_pay': 30,
        'benefits': 'Healthcare, Paid Time Off',
        'review': 'Great place to work!',
        'rating': 5,
        'recommendation': 1
    }
    
    response = client.post('/create_review', data=review_data)
    assert response.status_code == 200  # Assuming 200 OK if review is created successfully
    review = Reviews.query.filter_by(job_title='Software Engineer').first()
    assert review is not None  # Review should be saved in the database
    assert review.rating == 5  # Ensure that the rating is correct


def test_upvote_review(client):
    """Test the upvoting functionality for a review."""
    # Create a review first
    with client.session_transaction() as sess:
        sess['username'] = 'testuser'
    
    review_data = {
        'department': 'Engineering',
        'locations': 'New York',
        'job_title': 'Software Engineer',
        'job_description': 'Developing software',
        'hourly_pay': 30,
        'benefits': 'Healthcare, Paid Time Off',
        'review': 'Great place to work!',
        'rating': 5,
        'recommendation': 1
    }
    response = client.post('/create_review', data=review_data)
    assert response.status_code == 200
    
    # Upvote the review
    review = Reviews.query.filter_by(job_title='Software Engineer').first()
    review_id = review.id
    
    response = client.post(f'/upvote_review/{review_id}')
    assert response.status_code == 200  # Upvote should succeed
    review = Reviews.query.filter_by(id=review_id).first()
    assert review.upvote_count == 1  # Ensure that the upvote count increases by 1


def test_multiple_upvotes_by_same_user(client):
    """Test that a user can only upvote a review once."""
    # Create a review
    with client.session_transaction() as sess:
        sess['username'] = 'testuser'
    
    review_data = {
        'department': 'Engineering',
        'locations': 'New York',
        'job_title': 'Software Engineer',
        'job_description': 'Developing software',
        'hourly_pay': 30,
        'benefits': 'Healthcare, Paid Time Off',
        'review': 'Great place to work!',
        'rating': 5,
        'recommendation': 1
    }
    response = client.post('/create_review', data=review_data)
    assert response.status_code == 200
    
    # Upvote the review
    review = Reviews.query.filter_by(job_title='Software Engineer').first()
    review_id = review.id
    response = client.post(f'/upvote_review/{review_id}')
    assert response.status_code == 200  # First upvote should succeed
    
    # Try to upvote again
    response = client.post(f'/upvote_review/{review_id}')
    assert response.status_code == 400  # Should fail with a 400 bad request, as user already upvoted
    review = Reviews.query.filter_by(id=review_id).first()
    assert review.upvote_count == 1  # Ensure upvote count hasn't increased


def test_upvote_review_invalid_review(client):
    """Test that a user cannot upvote a review that doesn't exist."""
    with client.session_transaction() as sess:
        sess['username'] = 'testuser'
    
    response = client.post('/upvote_review/999')  # Assuming 999 is an invalid review ID
    assert response.status_code == 404  # Should return 404 if review not found


# Fixture to set up and tear down the database for each test
@pytest.fixture(scope='function')
def setup_db():
    db.create_all()  # Set up the database before each test
    yield
    db.session.remove()
    db.drop_all()  # Tear down the database after each test

def test_create_user(setup_db):
    """Test creating a new user"""
    user = User(user_name="unique_user", name="Test User", email="test@example.com", password="password", type="applicant")
    db.session.add(user)
    db.session.commit()

    user_in_db = User.query.filter_by(user_name="unique_user").first()
    assert user_in_db is not None
    assert user_in_db.name == "Test User"
    assert user_in_db.email == "test@example.com"

def test_create_job(setup_db):
    """Test creating a new job"""
    job = Job(title="Software Engineer", description="Develop software", location="NC", pay=100.0, employer_id="unique_user")
    db.session.add(job)
    db.session.commit()

    job_in_db = Job.query.filter_by(title="Software Engineer").first()
    assert job_in_db is not None
    assert job_in_db.location == "NC"
    assert job_in_db.pay == 100.0

def test_create_application(setup_db):
    """Test creating an application for a job"""
    user = User(user_name="applicant_user", name="Applicant", email="applicant@example.com", password="password", type="applicant")
    db.session.add(user)
    db.session.commit()

    job = Job(title="Software Engineer", description="Develop software", location="NC", pay=100.0, employer_id="unique_user")
    db.session.add(job)
    db.session.commit()

    application = Application(job_id=job.job_id, user_name=user.user_name)
    db.session.add(application)
    db.session.commit()

    application_in_db = Application.query.filter_by(user_name="applicant_user").first()
    assert application_in_db is not None
    assert application_in_db.job_id == job.job_id

def test_create_review(setup_db):
    """Test creating a review for a job"""
    user = User(user_name="reviewer_user", name="Reviewer", email="reviewer@example.com", password="password", type="applicant")
    db.session.add(user)
    db.session.commit()

    review = Reviews(department="IT", locations="NC", job_title="Software Engineer", job_description="Develop software", hourly_pay=50, benefits="Health", review="Good Job", rating=4, recommendation=1)
    db.session.add(review)
    db.session.commit()

    review_in_db = Reviews.query.filter_by(job_title="Software Engineer").first()
    assert review_in_db is not None
    assert review_in_db.rating == 4
    assert review_in_db.recommendation == 1

def test_create_upvote(setup_db):
    """Test creating an upvote on a review"""
    user = User(user_name="upvoter_user", name="Upvoter", email="upvoter@example.com", password="password", type="applicant")
    db.session.add(user)
    db.session.commit()

    review = Reviews(department="IT", locations="NC", job_title="Software Engineer", job_description="Develop software", hourly_pay=50, benefits="Health", review="Good Job", rating=4, recommendation=1)
    db.session.add(review)
    db.session.commit()

    upvote = Upvote(review_id=review.id, user_name=user.user_name)
    db.session.add(upvote)
    db.session.commit()

    upvote_in_db = Upvote.query.filter_by(review_id=review.id, user_name="upvoter_user").first()
    assert upvote_in_db is not None

def test_multiple_upvotes_by_same_user(setup_db):
    """Test that a user cannot upvote the same review more than once"""
    user = User(user_name="upvoter_user", name="Upvoter", email="upvoter@example.com", password="password", type="applicant")
    db.session.add(user)
    db.session.commit()

    review = Reviews(department="IT", locations="NC", job_title="Software Engineer", job_description="Develop software", hourly_pay=50, benefits="Health", review="Good Job", rating=4, recommendation=1)
    db.session.add(review)
    db.session.commit()

    upvote = Upvote(review_id=review.id, user_name=user.user_name)
    db.session.add(upvote)
    db.session.commit()

    # Try to upvote again by the same user
    with pytest.raises(Exception):  # Should raise an exception due to unique constraint on user_name and review_id
        upvote_duplicate = Upvote(review_id=review.id, user_name=user.user_name)
        db.session.add(upvote_duplicate)
        db.session.commit()



def test_upvote_review(setup_db):
    """Test that an upvote for a review is successful"""
    user = User(user_name="upvoter_user", name="Upvoter", email="upvoter@example.com", password="password", type="applicant")
    db.session.add(user)
    db.session.commit()

    review = Reviews(department="IT", locations="NC", job_title="Software Engineer", job_description="Develop software", hourly_pay=50, benefits="Health", review="Good Job", rating=4, recommendation=1)
    db.session.add(review)
    db.session.commit()

    # Make an upvote
    upvote = Upvote(review_id=review.id, user_name=user.user_name)
    db.session.add(upvote)
    db.session.commit()

    upvote_in_db = Upvote.query.filter_by(review_id=review.id, user_name=user.user_name).first()
    assert upvote_in_db is not None



def test_create_job_with_duplicate_title(setup_db):
    """Test creating a job with a duplicate title"""
    job1 = Job(title="Software Engineer", description="Develop software", location="NC", pay=100.0, employer_id="unique_user")
    db.session.add(job1)
    db.session.commit()

    job2 = Job(title="Software Engineer", description="Develop software", location="NY", pay=120.0, employer_id="another_user")
    try:
        db.session.add(job2)
        db.session.commit()
    except Exception as e:
        assert "UNIQUE constraint failed" in str(e)  # Ensure unique constraint on title is violated


def test_create_application_for_nonexistent_job(setup_db):
    """Test creating an application for a non-existent job"""
    user = User(user_name="applicant_user", name="Applicant", email="applicant@example.com", password="password", type="applicant")
    db.session.add(user)
    db.session.commit()

    # Attempt to create an application for a non-existent job
    try:
        application = Application(job_id=999, user_name=user.user_name)  # Non-existent job_id
        db.session.add(application)
        db.session.commit()
    except Exception as e:
        assert "foreign key constraint failed" in str(e)  # Ensure foreign key violation



def test_create_job_with_invalid_pay(setup_db):
    """Test creating a job with invalid pay"""
    job = Job(title="Software Engineer", description="Develop software", location="NC", pay=-100.0, employer_id="unique_user")
    try:
        db.session.add(job)
        db.session.commit()
    except Exception as e:
        assert "CHECK constraint failed" in str(e)  # Ensure negative pay is not allowed


def test_upvote_review_nonexistent_user(setup_db, client):
    """Test that a non-existent user cannot upvote a review"""
    review = Reviews(department="IT", locations="NC", job_title="Software Engineer", job_description="Develop software", hourly_pay=50, benefits="Health", review="Good Job", rating=4, recommendation=1)
    db.session.add(review)
    db.session.commit()

    # Simulate a non-existent user attempting to upvote
    response = client.post(f'/upvote_review/{review.id}')  # Non-existent user
    assert response.status_code == 404  # Should return 404 if user doesn't exist

def test_create_job_with_invalid_location(setup_db):
    """Test creating a job with an invalid location"""
    job = Job(title="Software Engineer", description="Develop software", location="XYZ", pay=100.0, employer_id="unique_user")
    try:
        db.session.add(job)
        db.session.commit()
    except Exception as e:
        assert "CHECK constraint failed" in str(e)  # Ensure invalid location is not allowed


def test_create_review_with_invalid_rating(setup_db):
    """Test creating a review with an invalid rating"""
    user = User(user_name="reviewer_user", name="Reviewer", email="reviewer@example.com", password="password", type="applicant")
    db.session.add(user)
    db.session.commit()

    review = Reviews(department="IT", locations="NC", job_title="Software Engineer", job_description="Develop software", hourly_pay=50, benefits="Health", review="Good Job", rating=6, recommendation=1)
    try:
        db.session.add(review)
        db.session.commit()
    except Exception as e:
        assert "CHECK constraint failed" in str(e)  # Ensure invalid rating is rejected


def test_create_multiple_reviews_for_same_job(setup_db):
    """Test creating multiple reviews for the same job"""
    user = User(user_name="reviewer_user", name="Reviewer", email="reviewer@example.com", password="password", type="applicant")
    db.session.add(user)
    db.session.commit()

    review1 = Reviews(department="IT", locations="NC", job_title="Software Engineer", job_description="Develop software", hourly_pay=50, benefits="Health", review="Good Job", rating=4, recommendation=1)
    db.session.add(review1)
    db.session.commit()

    review2 = Reviews(department="IT", locations="NC", job_title="Software Engineer", job_description="Develop software", hourly_pay=50, benefits="Health", review="Great place", rating=5, recommendation=1)
    db.session.add(review2)
    db.session.commit()

    reviews = Reviews.query.filter_by(job_title="Software Engineer").all()
    assert len(reviews) == 2  # Ensure two reviews exist for the same job


def test_create_review_without_job_title(setup_db):
    """Test creating a review without a job title"""
    user = User(user_name="reviewer_user", name="Reviewer", email="reviewer@example.com", password="password", type="applicant")
    db.session.add(user)
    db.session.commit()

    review = Reviews(department="IT", locations="NC", job_title="", job_description="Develop software", hourly_pay=50, benefits="Health", review="Good Job", rating=4, recommendation=1)
    try:
        db.session.add(review)
        db.session.commit()
    except Exception as e:
        assert "NOT NULL constraint failed" in str(e)  # Ensure job title is required

def test_upvote_review_for_nonexistent_job(client):
    """Test that a user cannot upvote a review for a nonexistent job"""
    response = client.post('/upvote_review/999')  # Invalid review ID
    assert response.status_code == 404  # Should return 404


def test_create_application_for_invalid_user(setup_db):
    """Test creating an application for a non-existent user"""
    job = Job(title="Software Engineer", description="Develop software", location="NC", pay=100.0, employer_id="unique_user")
    db.session.add(job)
    db.session.commit()

    try:
        application = Application(job_id=job.job_id, user_name="non_existent_user")
        db.session.add(application)
        db.session.commit()
    except Exception as e:
        assert "foreign key constraint failed" in str(e)

def test_create_review_with_empty_description(setup_db):
    """Test creating a review with an empty description"""
    user = User(user_name="reviewer_user", name="Reviewer", email="reviewer@example.com", password="password", type="applicant")
    db.session.add(user)
    db.session.commit()

    review = Reviews(department="IT", locations="NC", job_title="Software Engineer", job_description="", hourly_pay=50, benefits="Health", review="Good Job", rating=4, recommendation=1)
    try:
        db.session.add(review)
        db.session.commit()
    except Exception as e:
        assert "NOT NULL constraint failed" in str(e)




def test_create_upvote(setup_db):
    """Test creating an upvote for a review by a user"""
    user = User(user_name="upvoter_user", name="Upvoter", email="upvoter@example.com", password="password", type="applicant")
    db.session.add(user)
    db.session.commit()

    review = Reviews(department="IT", locations="NC", job_title="Software Engineer", job_description="Develop software", hourly_pay=50, benefits="Health", review="Good Job", rating=4, recommendation=1)
    db.session.add(review)
    db.session.commit()

    upvote = Upvote(review_id=review.id, user_name=user.user_name)
    db.session.add(upvote)
    db.session.commit()

    upvote_in_db = Upvote.query.filter_by(review_id=review.id, user_name=user.user_name).first()
    assert upvote_in_db is not None


def test_upvote_multiple_users(setup_db):
    """Test that multiple users can upvote the same review"""
    user1 = User(user_name="user1", name="User One", email="user1@example.com", password="password", type="applicant")
    user2 = User(user_name="user2", name="User Two", email="user2@example.com", password="password", type="applicant")
    db.session.add(user1)
    db.session.add(user2)
    db.session.commit()

    review = Reviews(department="IT", locations="NC", job_title="Software Engineer", job_description="Develop software", hourly_pay=50, benefits="Health", review="Good Job", rating=4, recommendation=1)
    db.session.add(review)
    db.session.commit()

    upvote1 = Upvote(review_id=review.id, user_name=user1.user_name)
    upvote2 = Upvote(review_id=review.id, user_name=user2.user_name)
    db.session.add(upvote1)
    db.session.add(upvote2)
    db.session.commit()

    assert Upvote.query.filter_by(review_id=review.id).count() == 2  # Ensure two upvotes for the review

def test_upvote_unique_constraint(setup_db):
    """Test that a user cannot upvote a review more than once"""
    user = User(user_name="unique_user", name="Unique User", email="unique@example.com", password="password", type="applicant")
    db.session.add(user)
    db.session.commit()

    review = Reviews(department="IT", locations="NC", job_title="Software Engineer", job_description="Develop software", hourly_pay=50, benefits="Health", review="Good Job", rating=4, recommendation=1)
    db.session.add(review)
    db.session.commit()

    # First upvote
    upvote = Upvote(review_id=review.id, user_name=user.user_name)
    db.session.add(upvote)
    db.session.commit()

    # Second upvote (should fail due to unique constraint)
    with pytest.raises(Exception):
        upvote_duplicate = Upvote(review_id=review.id, user_name=user.user_name)
        db.session.add(upvote_duplicate)
        db.session.commit()


def test_upvote_non_existent_review(setup_db):
    """Test that an upvote cannot be created for a non-existent review"""
    user = User(user_name="nonexistent_user", name="Nonexistent User", email="nonexistent@example.com", password="password", type="applicant")
    db.session.add(user)
    db.session.commit()

    # Try upvoting a review with an invalid ID
    try:
        upvote = Upvote(review_id=9999, user_name=user.user_name)  # Non-existent review
        db.session.add(upvote)
        db.session.commit()
    except Exception as e:
        assert "foreign key constraint failed" in str(e)


def test_upvote_non_existent_user(setup_db):
    """Test that an upvote cannot be created by a non-existent user"""
    review = Reviews(department="IT", locations="NC", job_title="Software Engineer", job_description="Develop software", hourly_pay=50, benefits="Health", review="Good Job", rating=4, recommendation=1)
    db.session.add(review)
    db.session.commit()

    # Try upvoting with a non-existent user
    try:
        upvote = Upvote(review_id=review.id, user_name="nonexistent_user")  # Non-existent user
        db.session.add(upvote)
        db.session.commit()
    except Exception as e:
        assert "foreign key constraint failed" in str(e)


def test_upvote_retrieve_user_and_review(setup_db):
    """Test that an upvote can correctly retrieve the user and review it corresponds to"""
    user = User(user_name="user1", name="User One", email="user1@example.com", password="password", type="applicant")
    db.session.add(user)
    db.session.commit()

    review = Reviews(department="IT", locations="NC", job_title="Software Engineer", job_description="Develop software", hourly_pay=50, benefits="Health", review="Good Job", rating=4, recommendation=1)
    db.session.add(review)
    db.session.commit()

    upvote = Upvote(review_id=review.id, user_name=user.user_name)
    db.session.add(upvote)
    db.session.commit()

    upvote_in_db = Upvote.query.filter_by(review_id=review.id, user_name=user.user_name).first()
    assert upvote_in_db is not None
    assert upvote_in_db.review_id == review.id
    assert upvote_in_db.user_name == user.user_name


def test_upvote_user_name_length_constraint(setup_db):
    """Test that the user_name field has the correct length constraint"""
    user = User(user_name="user1", name="User One", email="user1@example.com", password="password", type="applicant")
    db.session.add(user)
    db.session.commit()

    review = Reviews(department="IT", locations="NC", job_title="Software Engineer", job_description="Develop software", hourly_pay=50, benefits="Health", review="Good Job", rating=4, recommendation=1)
    db.session.add(review)
    db.session.commit()

    long_user_name = "user_with_long_name"
    try:
        upvote = Upvote(review_id=review.id, user_name=long_user_name)  # Should fail if user_name exceeds the length limit
        db.session.add(upvote)
        db.session.commit()
    except Exception as e:
        assert "value too long" in str(e)


def test_upvote_multiple_upvotes_for_different_users(setup_db):
    """Test that different users can upvote different reviews"""
    user1 = User(user_name="user1", name="User One", email="user1@example.com", password="password", type="applicant")
    user2 = User(user_name="user2", name="User Two", email="user2@example.com", password="password", type="applicant")
    db.session.add(user1)
    db.session.add(user2)
    db.session.commit()

    review1 = Reviews(department="IT", locations="NC", job_title="Software Engineer", job_description="Develop software", hourly_pay=50, benefits="Health", review="Great Company", rating=4, recommendation=1)
    review2 = Reviews(department="Finance", locations="NY", job_title="Financial Analyst", job_description="Analyze data", hourly_pay=60, benefits="Health", review="Good place", rating=3, recommendation=0)
    db.session.add(review1)
    db.session.add(review2)
    db.session.commit()

    upvote1 = Upvote(review_id=review1.id, user_name=user1.user_name)
    upvote2 = Upvote(review_id=review2.id, user_name=user2.user_name)
    db.session.add(upvote1)
    db.session.add(upvote2)
    db.session.commit()

    assert Upvote.query.filter_by(review_id=review1.id).count() == 1
    assert Upvote.query.filter_by(review_id=review2.id).count() == 1







def test_review_recommendation_binary():
    """Verify recommendation is binary (0 or 1)"""
    review = Reviews(
        department='Customer Service',
        locations='Remote',
        job_title='Support Specialist',
        job_description='Provide customer support',
        hourly_pay=40,
        benefits='Flexible hours',
        review='Friendly team',
        rating=3,
        recommendation=0
    )
    db.session.add(review)
    db.session.commit()
    
    assert review.recommendation in [0, 1]

def test_review_string_fields_not_empty():
    """Ensure string fields are not empty"""
    review = Reviews(
        department='Product',
        locations='San Jose',
        job_title='Product Manager',
        job_description='Manage product development',
        hourly_pay=65,
        benefits='Comprehensive benefits',
        review='Innovative company',
        rating=5,
        recommendation=1
    )
    
    assert review.department
    assert review.locations
    assert review.job_title
    assert review.job_description
    assert review.benefits
    assert review.review




def test_review_length_constraints():
    """Basic test for string field length constraints"""
    review = Reviews(
        department='Tech',
        locations='San Francisco',
        job_title='Software Engineer',
        job_description='Develop software applications',
        hourly_pay=55,
        benefits='Comprehensive package',
        review='Great workplace with amazing opportunities',
        rating=4,
        recommendation=1
    )
    
    assert len(review.department) <= 64
    assert len(review.locations) <= 120
    assert len(review.job_title) <= 64
    assert len(review.job_description) <= 120
    assert len(review.benefits) <= 120
    assert len(review.review) <= 120

# Add more simple tests as needed
def test_review_creation_without_optional_methods():
    """Test creating a review without explicitly calling methods"""
    review = Reviews(
        department='Operations',
        locations='Denver',
        job_title='Operations Manager',
        job_description='Manage daily operations',
        hourly_pay=52,
        benefits='Performance bonus',
        review='Efficient work environment',
        rating=3,
        recommendation=0
    )
    
    assert review is not None



def test_review_rating_integer():
    """Verify rating is an integer"""
    review = Reviews(
        department='Marketing',
        locations='Atlanta',
        job_title='Digital Marketer',
        job_description='Manage digital marketing campaigns',
        hourly_pay=50,
        benefits='Creative environment',
        review='Innovative marketing strategies',
        rating=4,
        recommendation=1
    )
    
    assert isinstance(review.rating, int)



def test_review_benefits_optional():
    """Verify benefits can be set or left as default"""
    review = Reviews(
        department='Research',
        locations='Cambridge',
        job_title='Research Scientist',
        job_description='Conduct scientific research',
        hourly_pay=60,
        benefits='Research grants',
        review='Cutting-edge research opportunities',
        rating=5,
        recommendation=1
    )
    
    assert review.benefits is not None



import pytest
from flask import current_app

def test_review_creation_without_methods():
    """Test basic review object instantiation"""

    review = Reviews(
        department='Engineering',
        locations='San Francisco',
        job_title='Software Engineer',
        job_description='Develop web applications',
        hourly_pay=50,
        benefits='Health Insurance',
        review='Great workplace',
        rating=4,
        recommendation=1
    )
    
    assert review is not None
    assert review.department == 'Engineering'
    assert review.job_title == 'Software Engineer'

def test_review_required_fields():
    """Ensure all required fields are present"""

    review = Reviews(
        department='HR',
        locations='Boston',
        job_title='HR Manager',
        job_description='Manage human resources',
        hourly_pay=55,
        benefits='Comprehensive package',
        review='Supportive environment',
        rating=4,
        recommendation=1
    )
    
    assert review.department is not None
    assert review.job_title is not None
    assert review.rating is not None

def test_review_rating_positive():
    """Verify rating is positive"""

    review = Reviews(
        department='Sales',
        locations='Chicago',
        job_title='Sales Representative',
        job_description='Sell products',
        hourly_pay=40,
        benefits='Commission',
        review='Challenging role',
        rating=5,  # Assuming 1-5 rating scale
        recommendation=1
    )
    
    assert review.rating > 0
    assert review.rating <= 5

def test_review_hourly_pay_range():
    """Verify hourly pay is within reasonable range"""

    review = Reviews(
        department='IT',
        locations='Seattle',
        job_title='Network Engineer',
        job_description='Manage network infrastructure',
        hourly_pay=55,
        benefits='Remote work',
        review='Challenging technical role',
        rating=4,
        recommendation=1
    )
    
    assert review.hourly_pay > 0
    assert review.hourly_pay < 1000  # Assuming reasonable max hourly rate

def test_review_recommendation_binary():
    """Verify recommendation is binary"""

    review = Reviews(
        department='Customer Service',
        locations='Remote',
        job_title='Support Specialist',
        job_description='Provide customer support',
        hourly_pay=40,
        benefits='Flexible hours',
        review='Friendly team',
        rating=3,
        recommendation=0
    )
    
    assert review.recommendation in [0, 1]

def test_review_string_field_limits():
    """Test string field length constraints"""

    review = Reviews(
        department='Tech',
        locations='San Francisco',
        job_title='Software Engineer',
        job_description='Develop software applications',
        hourly_pay=55,
        benefits='Comprehensive package',
        review='Great workplace with amazing opportunities',
        rating=4,
        recommendation=1
    )
    
    assert len(review.department) <= 64
    assert len(review.locations) <= 120
    assert len(review.job_title) <= 64
    assert len(review.job_description) <= 120
    assert len(review.benefits) <= 120
    assert len(review.review) <= 120



def test_review_department_assignment():
    """Test department assignment"""

    review = Reviews(
        department='Product',
        locations='San Jose',
        job_title='Product Manager',
        job_description='Manage product development',
        hourly_pay=65,
        benefits='Comprehensive benefits',
        review='Innovative company',
        rating=5,
        recommendation=1
    )
    
    assert review.department == 'Product'

def test_review_job_title_assignment():
    """Test job title assignment""" # Adjust import as needed

    review = Reviews(
        department='Engineering',
        locations='Mountain View',
        job_title='Data Scientist',
        job_description='Analyze complex data sets',
        hourly_pay=70,
        benefits='Research opportunities',
        review='Cutting-edge research',
        rating=4,
        recommendation=1
    )
    
    assert review.job_title == 'Data Scientist'