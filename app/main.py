# app/main.py
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

# Mount the static directory
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Set up templates (point to the templates folder)
templates = Jinja2Templates(directory="app/templates")

@app.get("/")
async def read_index(request: Request):
    """
    Renders the homepage which loads the hero (index) component.
    """
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/plan-a-trip")
async def read_create_trip(request: Request):
    """
    Renders the trip planner page.
    """
    return templates.TemplateResponse("create_trip.html", {"request": request})
