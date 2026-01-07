from pathlib import Path
from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from .database import get_db
from . import models

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))



# @router.get("/resources/create/builder")
# def course_builder(request: Request):
 #   return templates.TemplateResponse(
 #       "course_builder.html",
  #      {"request": request},
  #  ) 

@router.get("/resources/create")
def create_choice(request: Request):
    return templates.TemplateResponse("create_choice.html", {"request": request})


@router.get("/resources/builder")
def course_builder(
    request: Request,
    title: str = "",
    layout: str = "multi",
):
    return templates.TemplateResponse(
        "course_builder.html",
        {
            "request": request,
            "title": title,
            "layout": layout,
        },
    )


@router.get("/resources/new")
def new_resource_form(request: Request):
    return templates.TemplateResponse("new_resource.html", {"request": request})



@router.get("/resources/{resource_id}")
def view_resource(resource_id: int, request: Request, db: Session = Depends(get_db)):
    resource = db.query(models.Resource).filter_by(id=resource_id).first()
    if not resource:
        return RedirectResponse(url="/resources", status_code=303)

    invites = (
        db.query(models.CollaborationInvite)
        .filter(models.CollaborationInvite.resource_id == resource_id)
        .order_by(models.CollaborationInvite.created_at.desc())
        .all()
    )

    return templates.TemplateResponse(
        "resource_detail.html",
        {"request": request, "resource": resource, "invites": invites},
    )



@router.get("/resources")
def list_resources(request: Request, db: Session = Depends(get_db)):
    resources = db.query(models.Resource).all()
    return templates.TemplateResponse(
        "resources_list.html",
        {"request": request, "resources": resources},
    )





@router.post("/resources/new")
def create_resource(
    request: Request,
    title: str = Form(...),
    description: str = Form(""),
    content: str = Form(...),
    author_name: str = Form(...),
    author_email: str = Form(...),
    institution: str = Form(...),
    license: str = Form("CC BY"),

    # OPTIONAL: invite collaborator directly on create page
    collaborator_email: str = Form(""),
    message: str = Form(""),

    db: Session = Depends(get_db),
):
    # get or create user
    user = db.query(models.User).filter_by(email=author_email).first()
    if not user:
        user = models.User(
            name=author_name,
            email=author_email,
            institution=institution,
            role="author",
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    # create resource (draft)
    resource = models.Resource(
        title=title,
        description=description,
        license=license,
        created_by_id=user.id,
        status="draft",
    )
    db.add(resource)
    db.commit()
    db.refresh(resource)

    # version 1
    version = models.ResourceVersion(
        resource_id=resource.id,
        version_number=1,
        content=content,
        created_by_id=user.id,
    )
    db.add(version)
    db.commit()

    # OPTIONAL: create invite right away (early co-creation)
    if collaborator_email.strip():
        invite = models.CollaborationInvite(
            resource_id=resource.id,
            collaborator_email=collaborator_email.strip(),
            message=message.strip(),
            status="pending",
        )
        db.add(invite)
        db.commit()

    return RedirectResponse(url=f"/resources/{resource.id}", status_code=303)




@router.post("/resources/{resource_id}/submit-review")
def submit_for_review(resource_id: int, db: Session = Depends(get_db)):
    resource = db.query(models.Resource).filter_by(id=resource_id).first()
    if resource and resource.status == "draft":
        resource.status = "in_review"
        db.commit()
    return RedirectResponse(url=f"/resources/{resource_id}", status_code=303)


@router.post("/resources/{resource_id}/invite")
def invite_collaborator(
    resource_id: int,
    request: Request,
    collaborator_email: str = Form(...),
    message: str = Form(""),
    db: Session = Depends(get_db),
):
    resource = db.query(models.Resource).filter(models.Resource.id == resource_id).first()
    if not resource:
        return RedirectResponse(url="/resources", status_code=303)

    invite = models.CollaborationInvite(
        resource_id=resource_id,
        collaborator_email=collaborator_email.strip(),
        message=message.strip(),
        status="pending",
    )
    db.add(invite)
    db.commit()

    return RedirectResponse(url=f"/resources/{resource_id}", status_code=303)



