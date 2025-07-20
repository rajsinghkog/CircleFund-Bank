from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os

app = FastAPI()

# Import API routes under /api
from app.api import routes
app.include_router(routes.router, prefix="/api")

# Mount static files for React build
app.mount(
    "/",
    StaticFiles(directory=os.path.join(os.path.dirname(__file__), "..", "frontend", "build"), html=True),
    name="react"
)

# Mount static files for other assets (if needed)
app.mount('/static', StaticFiles(directory='static'), name='static')

# Jinja2 templates (if still needed)
templates = Jinja2Templates(directory='templates')
