"""
Shared async email utility.
Configure via environment variables — works across all services.

Required env vars:
    SMTP_HOST     — e.g. smtp.gmail.com
    SMTP_PORT     — e.g. 587
    SMTP_USER     — your email address
    SMTP_PASSWORD — your email password / app password
    SMTP_FROM     — sender display name + address, e.g. "AI Recruitment <no-reply@example.com>"
"""

import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import aiosmtplib
from dotenv import load_dotenv

load_dotenv()

SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER: str = os.getenv("SMTP_USER", "")
SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM: str = os.getenv("SMTP_FROM", SMTP_USER)


async def send_email(
    to: str | list[str],
    subject: str,
    body: str,
    html: bool = False,
) -> None:
    """
    Send an email to one or multiple recipients.

    Args:
        to:      Single email address or list of addresses.
        subject: Email subject line.
        body:    Email body — plain text or HTML depending on `html` flag.
        html:    If True, send body as HTML. Defaults to plain text.

    Raises:
        aiosmtplib.SMTPException: on connection / auth / send failure.
    """
    recipients = [to] if isinstance(to, str) else to

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = SMTP_FROM
    message["To"] = ", ".join(recipients)

    mime_type = "html" if html else "plain"
    message.attach(MIMEText(body, mime_type, "utf-8"))

    await aiosmtplib.send(
        message,
        hostname=SMTP_HOST,
        port=SMTP_PORT,
        username=SMTP_USER,
        password=SMTP_PASSWORD,
        start_tls=True,
    )


async def send_welcome_email(to: str, name: str) -> None:
    """Send a welcome email after successful registration."""
    await send_email(
        to=to,
        subject="Welcome to AI Recruitment Platform",
        body=f"""
        <h2>Welcome, {name}!</h2>
        <p>Your account has been successfully created.</p>
        <p>You can now log in and start using the platform.</p>
        """,
        html=True,
    )


async def send_application_confirmation(
    to: str, candidate_name: str, job_title: str
) -> None:
    """Send a confirmation email when a candidate applies for a job."""
    await send_email(
        to=to,
        subject=f"Application Received — {job_title}",
        body=f"""
        <h2>Hi {candidate_name},</h2>
        <p>We have received your application for <strong>{job_title}</strong>.</p>
        <p>Our team will review your profile and get back to you shortly.</p>
        """,
        html=True,
    )


async def send_application_status_update(
    to: str, candidate_name: str, job_title: str, status: str
) -> None:
    """Notify candidate about a change in their application status."""
    status_messages = {
        "reviewed": "Your application is currently being reviewed by our HR team.",
        "accepted": "Congratulations! Your application has been <strong>accepted</strong>.",
        "rejected": "After careful consideration, we regret to inform you that your application was not selected at this time.",
    }
    message = status_messages.get(status, f"Your application status has been updated to: {status}.")

    await send_email(
        to=to,
        subject=f"Application Update — {job_title}",
        body=f"""
        <h2>Hi {candidate_name},</h2>
        <p>Regarding your application for <strong>{job_title}</strong>:</p>
        <p>{message}</p>
        """,
        html=True,
    )
