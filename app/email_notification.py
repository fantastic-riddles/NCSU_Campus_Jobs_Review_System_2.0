import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

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
        
        mssg = mssg.replace("<username>", username).replace("<password>", password)
        
        message = Mail(
        from_email='meetvora090201@gmail.com',
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
        return status, 400