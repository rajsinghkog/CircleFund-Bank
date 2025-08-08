from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request

app = FastAPI()

# Import API routes under /api
from app.api import routes
app.include_router(routes.router, prefix="/api")

# Mount static files for HTML/JS assets
app.mount('/static', StaticFiles(directory='static'), name='static')

# Set up Jinja2 templates
templates = Jinja2Templates(directory="app/templates")


def make_template_handler(template_name: str):
    async def handler(request: Request):
        return templates.TemplateResponse(template_name, {"request": request})
    return handler


# Map paths to templates and register handlers programmatically
_template_routes = [
    ("/", "index.html"),
    ("/join_group", "join_group.html"),
    ("/create_group", "create_group.html"),
    ("/deposit", "deposit.html"),
    ("/repayment_tracker", "repayment_tracker.html"),
    ("/voting_dashboard", "voting_dashboard.html"),
    ("/loan_request", "loan_request.html"),
    ("/login", "login.html"),
    ("/signup", "signup.html"),
    ("/statement", "statement.html"),
]

for path, tpl in _template_routes:
    app.add_api_route(path, make_template_handler(tpl), methods=["GET"])


@app.get("/logout")
async def logout(request: Request):
    response = templates.TemplateResponse("logout.html", {"request": request})
    response.delete_cookie(key="user_id")
    return response

