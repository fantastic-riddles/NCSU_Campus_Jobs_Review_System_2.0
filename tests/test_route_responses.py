import pytest
import os
import sys
import warnings

sys.path.append(os.getcwd())
from app import db, app
from app.models import User, Job, Application, Reviews
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

def test_upvote_review_without_login(client):
    """Test upvote attempt without logging in."""
    response = client.post('/upvote/1')
    assert response.status_code == 302  # Redirect to login
    assert b'login' in response.headers['Location']


def test_upvote_review_nonexistent(client, db_session):
    """Test upvote attempt for a non-existent review."""
    with client.session_transaction() as sess:
        sess['username'] = 'regularuser'
    response = client.post('/upvote/999')
    assert response.status_code == 302
    assert b'page_content' in response.headers['Location']

def test_upvote_review_duplicate(client, db_session):
    """Test attempting to upvote a review multiple times."""
    with client.session_transaction() as sess:
        sess['username'] = 'regularuser'
    review = Reviews(id=1, upvote_count=0)
    upvote = Upvote(review_id=1, user_name='regularuser')
    db_session.add_all([review, upvote])
    db_session.commit()
    
    response = client.post('/upvote/1')
    assert response.status_code == 302
    assert review.upvote_count == 0

def test_upvote_review_by_admin(client, db_session):
    """Test upvote by an admin user."""
    with client.session_transaction() as sess:
        sess['username'] = 'admin'
        sess['type'] = 'admin'
    review = Reviews(id=1, upvote_count=0)
    db_session.add(review)
    db_session.commit()
    
    response = client.post('/upvote/1')
    assert response.status_code == 302
    assert review.upvote_count == 1

def test_upvote_review_invalid_session(client):
    """Test upvote attempt with an invalid session."""
    with client.session_transaction() as sess:
        sess['username'] = None
    response = client.post('/upvote/1')
    assert response.status_code == 302  # Redirect to login

def test_upvote_review_invalid_id(client, db_session):
    """Test upvote attempt with invalid review ID."""
    with client.session_transaction() as sess:
        sess['username'] = 'regularuser'
    response = client.post('/upvote/abc')
    assert response.status_code == 404

def test_upvote_review_count_unchanged_on_fail(client, db_session):
    """Ensure review upvote count doesn't change on failure."""
    with client.session_transaction() as sess:
        sess['username'] = 'regularuser'
    review = Reviews(id=1, upvote_count=0)
    db_session.add(review)
    db_session.commit()

    upvote = Upvote(review_id=1, user_name='regularuser')
    db_session.add(upvote)
    db_session.commit()

    response = client.post('/upvote/1')
    assert response.status_code == 302
    assert review.upvote_count == 0

def test_flash_message_duplicate_upvote(client, db_session):
    """Check if duplicate upvote displays the correct flash message."""
    with client.session_transaction() as sess:
        sess['username'] = 'regularuser'
    review = Reviews(id=1, upvote_count=0)
    upvote = Upvote(review_id=1, user_name='regularuser')
    db_session.add_all([review, upvote])
    db_session.commit()
    
    response = client.post('/upvote/1')
    assert b'You have already upvoted this review.' in response.data

def test_flash_message_successful_upvote(client, db_session):
    """Check flash message for a successful upvote."""
    with client.session_transaction() as sess:
        sess['username'] = 'regularuser'
    review = Reviews(id=1, upvote_count=0)
    db_session.add(review)
    db_session.commit()
    
    response = client.post('/upvote/1')
    assert b'Upvoted successfully!' in response.data

def test_upvote_review_multiple_users(client, db_session):
    """Test upvote count with multiple users."""
    review = Reviews(id=1, upvote_count=0)
    db_session.add(review)
    db_session.commit()

    for user in ['user1', 'user2', 'user3']:
        with client.session_transaction() as sess:
            sess['username'] = user
        client.post('/upvote/1')

    assert review.upvote_count == 3

def test_upvote_rollback_on_failure(client, db_session, monkeypatch):
    """Ensure database rolls back if commit fails."""
    with client.session_transaction() as sess:
        sess['username'] = 'regularuser'
    review = Reviews(id=1, upvote_count=0)
    db_session.add(review)
    db_session.commit()

    def fail_commit():
        raise Exception("Simulated commit failure")

    monkeypatch.setattr(db_session, 'commit', fail_commit)
    response = client.post('/upvote/1')

    assert review.upvote_count == 0

def test_upvote_by_guest_user(client):
    """Ensure a guest user cannot upvote."""
    response = client.post('/upvote/1')
    assert response.status_code == 302  # Redirect to login
    assert b'login' in response.headers['Location']

def test_upvote_archived_review(client, db_session):
    """Ensure upvotes cannot be added to archived reviews."""
    with client.session_transaction() as sess:
        sess['username'] = 'regularuser'
    review = Reviews(id=1, upvote_count=0, is_archived=True)
    db_session.add(review)
    db_session.commit()
    
    response = client.post('/upvote/1')
    assert response.status_code == 302
    assert review.upvote_count == 0

def test_upvote_empty_review_id(client):
    """Ensure upvote fails if review ID is empty."""
    response = client.post('/upvote/')
    assert response.status_code == 404  # Invalid URL

def test_upvote_redirect_to_correct_page(client, db_session):
    """Ensure upvote redirects to the correct page."""
    with client.session_transaction() as sess:
        sess['username'] = 'regularuser'
    review = Reviews(id=1, upvote_count=0)
    db_session.add(review)
    db_session.commit()
    
    response = client.post('/upvote/1')
    assert response.status_code == 302
    assert b'page_content' in response.headers['Location']

def test_upvote_db_downtime(client, db_session, monkeypatch):
    """Simulate database downtime and check error handling."""
    with client.session_transaction() as sess:
        sess['username'] = 'regularuser'
    review = Reviews(id=1, upvote_count=0)
    db_session.add(review)
    db_session.commit()

    def fail_commit():
        raise Exception("Database is down")

    monkeypatch.setattr(db_session, 'commit', fail_commit)
    response = client.post('/upvote/1')
    assert response.status_code == 302
    assert b'Error occurred' in response.data  # Check for custom error flash

def test_upvote_long_review_id(client):
    """Ensure upvote fails gracefully with an overly long review ID."""
    with client.session_transaction() as sess:
        sess['username'] = 'regularuser'
    long_id = 10**20  # Unreasonably large ID
    response = client.post(f'/upvote/{long_id}')
    assert response.status_code == 404

def test_multiple_upvotes_quick_succession(client, db_session):
    """Ensure upvote count remains correct despite rapid successive attempts."""
    with client.session_transaction() as sess:
        sess['username'] = 'regularuser'
    review = Reviews(id=1, upvote_count=0)
    db_session.add(review)
    db_session.commit()

    for _ in range(5):
        client.post('/upvote/1')

    assert review.upvote_count == 1

def test_upvote_csrf_protection(client):
    """Ensure CSRF protection is in place for upvote requests."""
    with client.session_transaction() as sess:
        sess['username'] = 'regularuser'
    
    # Simulate a CSRF token mismatch
    headers = {"X-CSRFToken": "invalid_token"}
    response = client.post('/upvote/1', headers=headers)
    assert response.status_code == 403  # Forbidden


