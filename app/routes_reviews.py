from fastapi import APIRouter

router = APIRouter()

from fastapi import APIRouter, Request, Depends, Form
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from .database import get_db
from . import models

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/reviews")
def list_reviews(request: Request, db: Session = Depends(get_db)):
    resources = db.query(models.Resource).filter_by(status="in_review").all()
    return templates.TemplateResponse(
        "reviews_list.html", {"request": request, "resources": resources}
    )


@router.get("/reviews/{resource_id}")
def review_detail(resource_id: int, request: Request, db: Session = Depends(get_db)):
    resource = db.query(models.Resource).filter_by(id=resource_id).first()
    if not resource:
        return RedirectResponse(url="/reviews", status_code=303)
    return templates.TemplateResponse(
        "review_detail.html", {"request": request, "resource": resource}
    )


@router.post("/reviews/{resource_id}/decision")
def review_decision(
    resource_id: int,
    decision: str = Form(...),  # 'approved' or 'changes_requested'
    comments: str = Form(""),
    db: Session = Depends(get_db),
):
    resource = db.query(models.Resource).filter_by(id=resource_id).first()
    if not resource:
        return RedirectResponse(url="/reviews", status_code=303)

    # Create a dummy reviewer user if none exists (prototype)
    reviewer = db.query(models.User).filter_by(role="reviewer").first()
    if not reviewer:
        reviewer = models.User(
            name="Test Reviewer",
            email="reviewer@example.com",
            institution="UiA",
            role="reviewer",
        )
        db.add(reviewer)
        db.commit()
        db.refresh(reviewer)

    review = models.Review(
        resource_id=resource.id,
        reviewer_id=reviewer.id,
        decision=decision,
        comments=comments,
    )
    db.add(review)

    resource.status = "approved" if decision == "approved" else "draft"
    db.commit()

    return RedirectResponse(url=f"/resources/{resource_id}", status_code=303)
