from mcp.server.fastmcp import FastMCP
import smtplib
import os
from dotenv import load_dotenv
from email.mime.text import MIMEText

load_dotenv()

mcp = FastMCP("Email Server")


@mcp.tool()
def send_email(receiver: str, subject: str, body: str) -> str:
    """
    Send an email using SMTP.

    IMPORTANT FOR THE AI ASSISTANT:

    - The assistant should generate the email subject and body.
    - The assistant MUST ask the user for the recipient's email address
      if it is not already known.
    - Do NOT call this tool until all three values are available:
        1. receiver
        2. subject
        3. body
    - After generating the email, ask the user for confirmation before
      calling this tool.
    """

    sender = os.getenv("EMAIL_ADDRESS")
    password = os.getenv("EMAIL_PASSWORD")
    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = os.getenv("SMTP_PORT")

    # Validate configuration
    if not sender:
        return "Error: EMAIL_ADDRESS is missing in the .env file."

    if not password:
        return "Error: EMAIL_APP_PASSWORD is missing in the .env file."

    if not smtp_server:
        return "Error: SMTP_SERVER is missing in the .env file."

    if not smtp_port:
        return "Error: SMTP_PORT is missing in the .env file."

    # Validate tool inputs
    if not receiver or "@" not in receiver:
        return (
            "Recipient email address is missing or invalid. "
            "The assistant should ask the user for the recipient's email "
            "before calling this tool."
        )

    if not subject:
        return "Subject cannot be empty."

    if not body:
        return "Email body cannot be empty."

    try:
        smtp_port = int(smtp_port)

        msg = MIMEText(body)
        msg["From"] = sender
        msg["To"] = receiver
        msg["Subject"] = subject

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender, password)
            server.sendmail(sender, receiver, msg.as_string())

        return f"Email successfully sent to {receiver}."

    except smtplib.SMTPAuthenticationError:
        return (
            "SMTP authentication failed. "
            "Verify EMAIL_ADDRESS and EMAIL_APP_PASSWORD."
        )

    except Exception as e:
        return f"Failed to send email: {e}"


if __name__ == "__main__":
    mcp.run()