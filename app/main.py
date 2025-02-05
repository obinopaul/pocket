# app/main.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from jinja2 import Template
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content
# from send_email import send_email_with_attachment, create_email_body  # Import the email functions
from app.send_email import send_email_with_attachment, create_email_body
from app.react_agent.pretty_print_2 import pretty_print_output
from dotenv import load_dotenv
import os
import asyncio
import uuid  # Added for unique filenames
from pathlib import Path  # Added for path handling
from app.react_agent.graph import PocketTraveller
import json # Added for JSON handling


# Load environment variables from the .env file
load_dotenv()

# Create data directory if not exists
Path("data").mkdir(exist_ok=True)

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
async def submit_trip(request: Request, data: TripFormData):
    try:
        user_input = {
            "origin": data.origin,
            "destination": data.destination,
            "dates": data.dates,
            "adults": data.adults,
            "children": data.children,
            "More Information": data.voiceNotes
        }

        # Convert user_input to string for the planner
        user_input_string = json.dumps(user_input)
        
        planner = PocketTraveller()
        output = await planner.invoke_graph(user_input_string )
        overview, flights, accommodations, activities, events, recommendations = pretty_print_output(output)
        
        all_tables = "\n\n".join(filter(None, [
            overview, flights, accommodations, activities, events, recommendations
        ]))

        # Load the template (results.html)
        with open("app/templates/results.html", "r") as file:
            template = Template(file.read())
            
        # Render the HTML content with the data (inject all_tables into the body)
        rendered_html = template.render(
            travel_plan=all_tables  # Inject the whole content into the body of the HTML
        )
    
        # Generate unique filename using UUID
        unique_id = uuid.uuid4().hex
        # document_filename = f"travel_plan_{unique_id}"
        file_path = f"app/static/results/{unique_id}.html"
        
        # Save the rendered HTML to a file
        with open(file_path, "w") as file:
            file.write(rendered_html)        

        # Get the base URL dynamically from the request
        base_url = str(request.base_url)  # This gives the base URL (e.g., http://127.0.0.1:8000/ or https://your-app.vercel.app/)
        
        # Construct the full URL for the generated webpage
        webpage_url = f"{base_url}static/results/{unique_id}.html"

        email_body = create_email_body(
            data.origin, 
            data.destination, 
            data.dates, 
            data.adults, 
            data.children,
            webpage_url
        )
        
        send_email_with_attachment(
            to_email=data.email, 
            subject="Your Pocket Travel Plan", 
            body=email_body, 
            webpage_url=webpage_url
        )
        
        return JSONResponse(content={"message": "Trip details received. An email will be sent shortly."})
    
    except Exception as e:
        print(f"Error in submit_trip: {e}")
        return JSONResponse(
            status_code=500, 
            content={"error": str(e)}
        )


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
