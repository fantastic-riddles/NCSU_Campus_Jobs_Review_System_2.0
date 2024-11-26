<h3 align="center">
Empower Your Future: Find Your Campus Opportunity with NCSU!
</h3>

<h2></h2>

<br>

The NCSU Campus Job Review System is a dynamic Flask application designed to empower students at North Carolina State University by providing a platform for reviewing, managing, and securing campus job opportunities. The system connects students with job listings, allows them to rate and review employers, and helps students easily find job opportunities that match their skills and aspirations.

## Key Features

- **Student Account Management**: Create an account, log in, and update your personal details.
- **Job Listings**: Browse campus job opportunities, view detailed descriptions, and apply directly.
- **Employer Reviews**: Rate and review employers based on work experience.
- **Search & Filters**: Find jobs based on job type, pay rate, or department.
- **Job Application Tracking**: Keep track of applied jobs and their status.
- **Email Notifications**: Get notified about new job listings and application updates via email.

## Technologies Used

- **Python** with **Flask** for web framework
- **SQLite** for lightweight database management
- **Twilio** for SMS notifications
- **Jinja2** for templating
- **Bootstrap** for frontend styling
- **Werkzeug** for handling security (password hashing)
- **Flask-Login** for session management
- **Flask-Mail** for email functionality

## Installation

To get started with the NCSU Campus Job Review System locally, follow these steps:

1. Clone the repository:
    ```bash
    git clone https://github.com/fantastic-riddles/NCSU_Campus_Jobs_Review_System_2.0.git
    cd NCSU_Campus_Jobs_Review_System_2.0
    ```

2. Set up a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4. Set up environment variables:
    - Create a `.env` file in the project root and add the necessary variables:
        ```
        FLASK_APP=app.py
        FLASK_ENV=development
        DATABASE_URL=sqlite:///database.db
        TWILIO_ACCOUNT_SID=your_twilio_account_sid
        TWILIO_AUTH_TOKEN=your_twilio_auth_token
        MAIL_USERNAME=your_email@example.com
        MAIL_PASSWORD=your_email_password
        ```

5. Initialize the database:
    ```bash
    flask db init
    flask db migrate
    flask db upgrade
    ```

6. Run the application:
    ```bash
    flask run
    ```

Your Flask application should now be running locally at `http://127.0.0.1:5000`.

## Usage

- **Sign Up / Log In**: Create an account to start browsing and applying for jobs.
- **Browse Jobs**: Filter jobs by category, department, or pay rate.
- **Review Employers**: Share your experience with past employers by leaving reviews.

## Contributing

We welcome contributions! Please fork the repository, create a new branch, make your changes, and submit a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Special thanks to the developers and contributors who have helped improve this system.