import sendgrid
from sendgrid.helpers.mail import Email, To, Content
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition
from base64 import b64encode
import os
import dotenv


dotenv.load_dotenv()

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")  # Replace with your actual SendGrid API Key
FROM_EMAIL = "paul.o.okafor-1@ou.edu"  # Replace with your email address


def send_email_with_attachment(to_email, subject, body, file_path):
    """
    Send an email with a PDF attachment using SendGrid.
    
    Args:
        to_email (str): The recipient's email address.
        subject (str): The subject of the email.
        body (str): The HTML body of the email.
        file_path (str): The path to the PDF file to attach.
    """
    
    try:
        sg = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)
    except Exception as e:
        print("Error initializing SendGrid client:", e)
        return

    try:
        # Use plain strings for from_email and to_emails.
        message = Mail(
            from_email=FROM_EMAIL,
            to_emails=to_email,
            subject=subject,
            html_content=body
        )
    except Exception as e:
        print("Error creating the Mail object:", e)
        return

    try:
        with open(file_path, "rb") as f:
            file_data = f.read()
        if not file_data:
            print("Attachment file is empty!")
            return
        encoded_file = b64encode(file_data).decode()
    except Exception as e:
        print(f"Error reading attachment file: {e}")
        return

    try:
        # Create the attachment using the new helper classes
        attachment = Attachment(
            FileContent(encoded_file),
            FileName(os.path.basename(file_path)),
            FileType("application/pdf"),
            Disposition("attachment")
        )
        # Attach the file to the message
        message.attachment = attachment
    except Exception as e:
        print("Error creating or adding attachment:", e)
        return

    try:
        response = sg.send(message)
    except Exception as e:
        print("Error sending email:", e)


# SendAPI has been blocked. I will get another one during the deployment.

def create_email_body(origin, destination, dates, adults, children):
    """
    Create a structured HTML email body with trip details.
    
    Args:
        origin (str): The origin of the trip.
        destination (str): The destination of the trip.
        dates (list[str]): The travel dates.
        adults (int): The number of adults.
        children (int): The number of children.
        
    Returns:
        str: The structured HTML body for the email.
    """
    body = f"""
    <html>
      <body>
        <h1>Pocket Travel - Your Trip Plan</h1>
        <p>Hi there,</p>
        <p>We are excited to present your travel plan. Please find the PDF attached to this email.</p>
        
        <h3>Trip Details:</h3>
        <ul>
          <li><strong>Origin:</strong> {origin}</li>
          <li><strong>Destination:</strong> {destination}</li>
          <li><strong>Travel Dates:</strong> {', '.join(dates)}</li>
          <li><strong>Adults:</strong> {adults}</li>
          <li><strong>Children:</strong> {children}</li>
        </ul>
        
        <p>If you have any questions, feel free to reach out to us.</p>
        
        <footer>
          <p>Best regards,</p>
          <p>The Pocket Travel Team</p>
        </footer>
      </body>
    </html>
    """
    return body

