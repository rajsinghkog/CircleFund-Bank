from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

# Mount static files
app.mount('/static', StaticFiles(directory='static'), name='static')

# Jinja2 templates
templates = Jinja2Templates(directory='templates')

# Import API routes
from app.api import routes
app.include_router(routes.router)

# Example root endpoint
@app.get('/')
def read_root():
    return {'message': 'Welcome to Community Lending Circle!'}
