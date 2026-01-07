from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from .database import get_db
from . import models

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


# 1) LMS "home" entry point (like H5P tool launch)
@router.get("/lti/openshare")
def lti_openshare_home(request: Request, db: Session = Depends(get_db)):
    """Entry point when Moodle launches OpenShare as a tool."""
    resources = db.query(models.Resource).all()
    return templates.TemplateResponse(
        "lti_openshare_home.html",
        {"request": request, "resources": resources},
    )


# 2) Generate or refresh LTI link for a specific resource
@router.post("/resources/{resource_id}/generate-link")
def generate_lti_link(resource_id: int, db: Session = Depends(get_db)):
    resource = db.query(models.Resource).filter_by(id=resource_id).first()
    if not resource or resource.status != "approved":
        return RedirectResponse(url=f"/resources/{resource_id}", status_code=303)

    # Check if link exists
    link = db.query(models.LtiLink).filter_by(resource_id=resource_id).first()
    if not link:
        # Store relative URL like "/lti/1"
        url = f"/lti/{resource_id}"
        link = models.LtiLink(resource_id=resource_id, url=url)
        db.add(link)
        db.commit()
        db.refresh(link)

    # Go back to the resource detail page (where the link is shown)
    return RedirectResponse(url=f"/resources/{resource_id}", status_code=303)


# 3) LTI-like launch for a specific resource
@router.get("/lti/{resource_id}")
def lti_launch(resource_id: int, request: Request, db: Session = Depends(get_db)):
    resource = db.query(models.Resource).filter_by(id=resource_id).first()
    if not resource or resource.status != "approved":
        return RedirectResponse(url="/", status_code=303)

    latest_version = resource.versions[-1] if resource.versions else None
    return templates.TemplateResponse(
        "lti_view.html",
        {"request": request, "resource": resource, "version": latest_version},
    )
