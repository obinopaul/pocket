# app/main.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content
from send_email import send_email_with_attachment, create_email_body  # Import the email functions
# from app.send_email import send_email_with_attachment, create_email_body
from dotenv import load_dotenv
import os


# Load environment variables from the .env file
load_dotenv()

# Retrieve the API key from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins, or specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)


# Mount the static folder so CSS, JS, images, etc. are accessible at /static
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Set up Jinja2 for HTML templating
templates = Jinja2Templates(directory="app/templates")

# Define a Pydantic model for form data validation
class TripFormData(BaseModel):
    origin: str
    destination: str
    dates: list[str]
    adults: int
    children: int
    email: str
    voiceNotes: str


        
# Endpoint to handle form submission and send data to the LLM
@app.post("/submit-trip")
async def submit_trip(data: TripFormData):
    # print(f"Received form data: {data}")
    pass

# async def submit_trip(data: TripFormData):
#     try:
#         print(f"Received form data: {data}")
        
#         document_path = "data/ayvaci2012.pdf.pdf"
        
#         email_body = create_email_body(
#             data.origin, 
#             data.destination, 
#             data.dates, 
#             data.adults, 
#             data.children
#         )
#         send_email_with_attachment(
#             to_email=data.email, 
#             subject="Your Pocket Travel Plan", 
#             body=email_body, 
#             file_path=document_path
#         )
#         return JSONResponse(content={"message": "Trip details received. An email will be sent shortly."})
    
#     except Exception as e:
#         print(f"Error in submit_trip: {e}")
#         return JSONResponse(
#             status_code=500, 
#             content={"error": str(e)}
#         )


# Homepage endpoint
@app.get("/")
async def read_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Trip planner page endpoint
@app.get("/plan-a-trip")
async def read_create_trip(request: Request):
    return templates.TemplateResponse("create_trip.html", {"request": request, "GOOGLE_MAPS_API_KEY": GOOGLE_MAPS_API_KEY})

@app.get("/thank-you")
async def read_create_trip(request: Request):
    return templates.TemplateResponse("thank_you.html", {"request": request})
# Run with: uvicorn app.main:app --reload
