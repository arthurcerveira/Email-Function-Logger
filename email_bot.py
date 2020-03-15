import smtplib
import os

from datetime import datetime, timedelta
from io import StringIO
from contextlib import redirect_stdout
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

ENVIRON_VAR = ['BOT_EMAIL', 'BOT_PASSWORD', 'LOG_RECIPIENT']


def log_info(function):
    email, password, recipient = get_email_info()
    session = authenticate_email(email, password)
    message = create_message(email, recipient)

    def log_function(*args, **kwargs):
        arguments = get_function_arguments(args, kwargs)

        # Add subject to email
        subject = f"Function '{function.__name__}' execution log"
        message['Subject'] = subject

        # Start email body text
        text = f"Function {function.__name__}({arguments}) finished its execution.\n\n"

        start_time = datetime.now()
        text += f"Start time: {start_time:%b %d %Y %H:%M:%S}\n"

        f = StringIO()
        with redirect_stdout(f):
            return_value = function(*args, **kwargs)
        text_output = f.getvalue()

        text += f'Function text output:\n{text_output}\n' if text_output else 'No text output\n'
        text += f'Function returned: {return_value}\n' if return_value else 'No returned value\n'

        end_time = datetime.now()
        text += f"End time: {end_time:%b %d %Y %H:%M:%S}\n"

        total = (end_time - start_time).seconds
        hours, remainder = divmod(total, 3600)
        minutes, seconds = divmod(remainder, 60)
        text += f'Total execution time: {hours:02d}:{minutes:02d}:{seconds:02d}\n'

        # Add body to email
        message.attach(MIMEText(text, 'plain'))
        body = message.as_string()

        session.sendmail(email, recipient, body)
        session.quit()

    return log_function


def get_email_info():
    email_info = dict()

    for var in ENVIRON_VAR:
        if os.environ.get(var):
            email_info[var] = os.environ.get(var)
        else:
            email_info[var] = input(f'{var}: ')

    return email_info['BOT_EMAIL'], email_info['BOT_PASSWORD'], email_info['LOG_RECIPIENT']


def authenticate_email(email, password):
    session = smtplib.SMTP('smtp.gmail.com', 587)
    session.starttls()
    session.login(email, password)

    return session


def create_message(email, recipient):
    message = MIMEMultipart()
    message['From'] = email
    message['To'] = recipient

    return message


def get_function_arguments(args, kwargs):
    args_repr = [repr(a) for a in args]
    kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
    arguments = ", ".join(args_repr + kwargs_repr)

    return arguments
