import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content, Attachment
from base64 import b64encode
import os
import dotenv


dotenv.load_dotenv()

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")  # Replace with your actual SendGrid API Key
FROM_EMAIL = "paul.o.okafor-1@ou.edu"  # Replace with your email address


def send_email_with_attachment(to_email, subject, body, webpage_url):
    """
    Send an email with an attachment using SendGrid.

    Args:
        to_email (str): The recipient's email address.
        subject (str): The subject of the email.
        body (str): The body text of the email.
        file_path (str): The file path to the document to be attached.
    """
    # Create a SendGrid client
    sg = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)

    # Create the email components
    from_email = Email(FROM_EMAIL)
    to_email = To(to_email)
    content = Content("text/html", body)  # Set the email body as HTML for structured content

    # Add a personalized link to the user's webpage
    body += f'<p>You can view your full travel plan at the following link: <a href="{webpage_url}">{webpage_url}</a></p>'
    
    # Prepare the email message
    mail = Mail(from_email, to_email, subject, content)

    # # Attach the document file
    # with open(file_path, "rb") as f:
    #     attachment = Attachment()
    #     attachment.content = b64encode(f.read()).decode()
    #     attachment.type = "application/pdf"  # Modify based on your file type
    #     attachment.filename = os.path.basename(file_path)
    #     attachment.disposition = "attachment"
    #     mail.add_attachment(attachment)

    # Send the email
    try:
        response = sg.send(mail)
        # print(f"Email sent successfully! Status code: {response.status_code}")
    except Exception as e:
        print(f"Error sending email: {e}")


def create_email_body(origin, destination, dates, adults, children, webpage_url):
    """
    Create a structured email body.

    Args:
        origin (str): The origin of the trip.
        destination (str): The destination of the trip.
        dates (str): The travel dates.
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
        <p>We are excited to present your travel plan. Below are the details of your trip:</p>
        
        <h3>Trip Details:</h3>
        <ul>
            <li><strong>Origin:</strong> {origin}</li>
            <li><strong>Destination:</strong> {destination}</li>
            <li><strong>Travel Dates:</strong> {dates}</li>
            <li><strong>Adults:</strong> {adults}</li>
            <li><strong>Children:</strong> {children}</li>
        </ul>

        <p>You can view your full travel plan at the following link: <a href="{webpage_url}">{webpage_url}</a></p>

        <p>If you have any questions, feel free to reach out to us.</p>

        <footer>
            <p>Best regards,</p>
            <p>The Pocket Travel Team</p>
        </footer>
    </body>
    </html>
    """
    return body
