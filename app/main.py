from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from fastapi import UploadFile, File
import os 


from .database import Base, engine
from . import routes_resources, routes_reviews, routes_lti

# Create all tables in the database (if they don't exist yet)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="OpenShare Prototype")
from pathlib import Path
print("MAIN.PY PATH =", Path(__file__).resolve())
print("CWD =", Path().resolve())
print("STATIC EXISTS? =", (Path(__file__).resolve().parent / "static" / "css" / "openshare.css").exists())


BASE_DIR = Path(__file__).resolve().parent

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount(
    "/static",
    StaticFiles(directory=str(BASE_DIR / "static")),
    name="static",
)


# Include route modules
app.include_router(routes_resources.router)
app.include_router(routes_reviews.router)
app.include_router(routes_lti.router)



@app.get("/")
def home():
    return RedirectResponse(url="/openshare-dashboard", status_code=303) 


@app.get("/openshare-dashboard", response_class=HTMLResponse)
async def openshare_dashboard(request: Request):
    resources = [
        {"title": "Cold Chain Management Module", "modified": "Jan 2025"},
        {"title": "Digital Literacy Starter Pack", "modified": "Dec 2024"},
        {"title": "Health Data Quality Lesson", "modified": "Nov 2024"},
    ]
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "resources": resources},
    )






