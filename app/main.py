from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
import os

app = FastAPI()

# Import API routes under /api
from app.api import routes
app.include_router(routes.router, prefix="/api")

# Mount static files for HTML/JS assets
app.mount('/static', StaticFiles(directory='static'), name='static')

# Set up Jinja2 templates
templates = Jinja2Templates(directory="app/templates")

# Example route using templates
@app.get("/")
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/join_group")
def join_group(request: Request):
    return templates.TemplateResponse("join_group.html", {"request": request})

@app.get("/deposit")
def deposit(request: Request):
    return templates.TemplateResponse("deposit.html", {"request": request})

@app.get("/repayment_tracker")
def repayment_tracker(request: Request):
    return templates.TemplateResponse("repayment_tracker.html", {"request": request})

@app.get("/voting_dashboard")
def voting_dashboard(request: Request):
    return templates.TemplateResponse("voting_dashboard.html", {"request": request})

@app.get("/loan_request")
def loan_request(request: Request):
    return templates.TemplateResponse("loan_request.html", {"request": request})

@app.get("/login")
def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/signup")
def signup(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

