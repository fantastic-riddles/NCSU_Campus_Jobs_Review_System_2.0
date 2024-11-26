import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import ssl

employer_mssg = f"""Hello,
<br>        
Welcome to the NCSU Job Portal! We're thrilled to have you on board. Here are your login credentials:
<br>
<br>
<b>Username</b>: <username>
<br>
<b>Password</b>: <password>
<br>
<br>
Upon logging in, you'll have access to features tailored for you, including:
<br><br>
<b>Post New Jobs:</b> Advertise open positions and find talented candidates.
<br>
<b>Review Applications:</b> Manage applications submitted for each position.
<br>
<br>
Should you have any questions, our support team is here to assist you.
<br><br>
Best regards,<br>
The NCSU Job Portal Team
"""

employee_mssg = f"""Hello,
        
Thank you for signing up for the NCSU Job Portal! We're excited to have you with us. Here are your login credentials to get started:
<br>
<br>
- <b>Username</b>: <username>
- <b>Password</b>: <password>
<br>
<br>
Please log in at your earliest convenience. You can now explore various job opportunities, submit applications, and post reviews.
<br><br>
Best of luck in your job search, <br>
The NCSU Job Portal Team
"""

new_job_alert_mssg = f"""Hello,

We have an exciting update for you on the NCSU Job Portal! A new job opportunity has just been posted. Here are the details:

<br><br>
- <b>Job Title:</b> <title>
- <b>Description:</b> <description>
- <b>Location:</b> <location>
- <b>Pay:</b> <pay>
<br><br>

Don’t miss out on this opportunity! Log in to the portal now to learn more and apply.

<br><br>
Best regards, <br>
The NCSU Job Portal Team
"""


def send_welcome_email(email, username, password, is_employee=False):
    """
    This function sends welcome message to user on signup

    Args:
        email: receiver email
        username: username of receiver
        password: password of receiver
        is_employee (default: false): send message based on role assumed by receiver

    Return:
        status: boolean indicating email success
        status_code: HTTP status code
    """

    status = False
    try:

        mssg = ""
        if is_employee:
            mssg = employee_mssg
        else:
            mssg = employer_mssg

        mssg = mssg.replace("<username>", username).replace(
            "<password>", password)

        # Temporarily disable SSL verification
        ssl._create_default_https_context = ssl._create_unverified_context

        message = Mail(
            from_email=os.environ.get('EMAIL_ADDRESS'),
            to_emails=email,
            subject='Welcome to NCSU Job Portal account!',
            html_content=f"{mssg}")

        sg = SendGridAPIClient(api_key=os.environ.get('EMAIL_API_KEY'))
        response = sg.send(message)

        if response.status_code == 200 or response.status_code == 202:
            status = True
            return status, 200
        else:
            return status, response.status_code

    except Exception as e:
        print("error sending email: ", e)
        return status, 400


def send_new_job_email(emails, title, description, location, pay):
    """
    This function sends welcome message to user on signup

    Args:
        email: receiver email
        username: username of receiver
        password: password of receiver
        is_employee (default: false): send message based on role assumed by receiver

    Return:
        status: boolean indicating email success
        status_code: HTTP status code
    """

    status = False
    try:

        mssg = new_job_alert_mssg
        mssg = mssg.replace("<title>", title).replace("<description>", description).replace("<location>", location).replace("<pay>", pay)

        # Temporarily disable SSL verification
        ssl._create_default_https_context = ssl._create_unverified_context

        message = Mail(
            from_email=os.environ.get('EMAIL_ADDRESS'),
            to_emails=emails,
            subject='New job added to NCSU job portal!',
            html_content=f"{mssg}")

        sg = SendGridAPIClient(api_key=os.environ.get('EMAIL_API_KEY'))
        response = sg.send(message)

        if response.status_code == 200 or response.status_code == 202:
            status = True
            return status, 200
        else:
            return status, response.status_code

    except Exception as e:
        print("error sending email: ", e)
        return status, 400
