import os
import smtplib
import frappe
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from frappe.utils.jinja import render_template
def send_zoho_mail(to_email, subject, message_body):
    """
    Sends an email using a Zoho SMTP account.

    Args:
        to_email (str): Recipient's email address
        subject (str): Email subject
        message_body (str): Email content (HTML or plain text)
    """
    
    # 🔄 Replace with your Zoho SMTP credentials
    SMTP_SERVER = "smtp.zoho.in"  # Zoho SMTP Server
    SMTP_PORT = 587  # Use 465 for SSL, 587 for TLS
    SMTP_USERNAME = "er1@bytepanda.in"  # Your Zoho email
    SMTP_PASSWORD = "h19FjsnpSnBh"  # Use App Password, not your login password
    FROM_EMAIL = SMTP_USERNAME  # Sender email (Zoho)
    
    try:
        # Create an email message
        msg = MIMEMultipart()
        msg["From"] = FROM_EMAIL
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(message_body, "html"))  # Use "plain" for plain text

        # Connect to the Zoho SMTP server
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.set_debuglevel(1)
        server.starttls()  # Secure the connection
        server.login(SMTP_USERNAME, SMTP_PASSWORD)  # Login to Zoho


        # Send the email
        server.sendmail(FROM_EMAIL, to_email, msg.as_string())

        # Close the connection
        server.quit()

        # frappe.msgprint(f"Email successfully sent to {to_email} 📩✅")
    
    except Exception as e:
        frappe.throw(f"Failed to send email: {str(e)} ❌")


def send_email(template_name, to_email, context, subject):
    try:
        print("template name: " + template_name)
        print(os.path.exists(f"templates/email/{template_name}.html"))  # Should print True

        print(context)
        email_body = render_template(f"templates/email/{template_name}.html", context)
        print(email_body)
    except Exception as e:
        frappe.throw(f"Error rendering email template: {str(e)}")

    send_zoho_mail(
        to_email=to_email,
        subject=subject,
        message_body=email_body
    )

