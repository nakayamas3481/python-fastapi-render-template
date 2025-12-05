from datetime import date
import os
from typing import Annotated, List, Optional
import uuid
from fastapi import BackgroundTasks, Body, Depends, FastAPI, File, Form, Request, HTTPException, Response, UploadFile, status
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field, field_validator
from ai import get_recommendation, get_vector_store, ingest_resume_for_recommendataions, review_application
from auth import AdminAuthzMiddleware, AdminSessionMiddleware, authenticate_admin, delete_admin_session, is_admin
from config import settings
from sqlalchemy import Date, create_engine, select, text
from sqlalchemy.orm import Session
from db import get_db_session
from emailer import send_email
from job_application_tasks import evaluate_resume
from models import JobApplication, JobBoard
from models import JobPost
from file_storage import upload_file

app = FastAPI()
app.add_middleware(AdminAuthzMiddleware)
app.add_middleware(AdminSessionMiddleware)

templates = Jinja2Templates(directory="templates")

app.mount("/assets", StaticFiles(directory="frontend/build/client/assets"))


if not settings.PRODUCTION:
    app.mount("/uploads", StaticFiles(directory="uploads"))

@app.get("/api/health")
async def health():
  try:
    with get_db_session() as session:
        session.execute(text("SELECT 1"))
        return {"database": "ok"}
  except:
    return {"database": "down"}
  
@app.get("/api/job-boards")
async def api_job_boards():
   with get_db_session() as session:
      jobBoards = session.query(JobBoard).all()
   return jobBoards  

@app.get("/")
async def root():
  return {"hello": "world"}

class JobBoardForm(BaseModel):
    slug : str = Field(..., min_length=3, max_length=20)
    logo : UploadFile = File(...)

    @field_validator('slug')
    @classmethod
    def to_lowercase(cls, v):
       return v.lower()

@app.post("/api/add")
async def api_create_new_add(x: Annotated[int, Form()], y: Annotated[int, Form()]):
    return {"slug":x+y}

@app.post("/api/json/add")
async def api_create_new_json_add(
    x: Annotated[int, Body()],
    y: Annotated[int, Body()],
):
    return {"slug": x + y}

@app.post("/api/job-boards")
async def api_create_new_job_board(request: Request, job_board_form: Annotated[JobBoardForm, Form()]):
    admin_token = request.cookies.get("admin_session")
    if not admin_token or not is_admin(admin_token):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin only"
        )

    logo_contents = await job_board_form.logo.read()

    _, ext = os.path.splitext(job_board_form.logo.filename)
    random_name = uuid.uuid4().hex
    randomized_filename = f"{random_name}{ext}"

    file_url = upload_file("company-logos", \
                           randomized_filename, \
                           logo_contents, \
                           job_board_form.logo.content_type)
    with get_db_session() as session:
        new_job_board = JobBoard(slug=job_board_form.slug, logo_url=file_url)
        session.add(new_job_board)
        session.commit()
        session.refresh(new_job_board)
        return new_job_board
    
@app.put("/api/job-boards/{job_board_id}")
async def api_update_job_board(job_board_id: int, slug: Annotated[Optional[str], Form()] = None, logo: Annotated[Optional[UploadFile], File()] = None,):
   with get_db_session() as session:
        jb = session.get(JobBoard, job_board_id)
        if not jb:
            raise HTTPException(status_code=404, detail="JobBoard not found")
        if slug is not None:
            jb.slug = slug
        if logo is not None:
            logo_contents = await logo.read()
            _, ext = os.path.splitext(logo.filename)
            randomized_filename = f"{uuid.uuid4().hex}{ext}"
            jb.logo_url = upload_file(
                "company-logos",
                randomized_filename,
                logo_contents,
                logo.content_type,
            )

        session.commit()
        session.refresh(jb)
        return jb
   
@app.delete("/api/job-boards/{job_board_id}")
async def api_delete_job_board(job_board_id: int):
    with get_db_session() as session:
        jb = session.get(JobBoard, job_board_id)
        if not jb:
            raise HTTPException(status_code=404, detail="JobBoard not found")
        session.delete(jb)
        session.commit()
        return jb

@app.get("/api/job-boards/{job_board_id}/job-posts")
async def api_company_job_board(job_board_id):
  with get_db_session() as session:
     jobPosts = session.query(JobPost).filter(JobPost.job_board_id.__eq__(job_board_id)).all()
     return jobPosts
  
class JobApplicationForm(BaseModel):
    firtst_name : str = Field(..., min_length=1, max_length=20)
    last_name : str = Field(..., min_length=1, max_length=20)
    email : str = Field(..., min_length=1, max_length=40)
    job_post_id : str = Field(..., min_length=1, max_length=20)
    resume : UploadFile = File(...)
  
@app.post("/api/job-applications")
async def api_create_new_job_application(job_application_form: Annotated[JobApplicationForm, Form()],background_tasks: BackgroundTasks,db: Session = Depends(get_db_session),vector_store = Depends(get_vector_store)):
    resume_contents = await job_application_form.resume.read()
    file_url = upload_file("company-resumes", \
                           job_application_form.resume.filename, \
                           resume_contents, \
                           job_application_form.resume.content_type)
    job_post = db.execute(
        select(JobPost).where(JobPost.id == job_application_form.job_post_id)
    ).scalar_one_or_none()

    if job_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job post not found")

    if job_post.close_date is not None and job_post.close_date < Date.today():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This job post is closed",
    )
    new_job_application = JobApplication(firtst_name=job_application_form.firtst_name, last_name=job_application_form.last_name, email=job_application_form.email,  job_post_id=job_application_form.job_post_id, resume_url=file_url)

    db.add(new_job_application)
    db.commit()
    db.refresh(new_job_application)

    background_tasks.add_task(
        send_email,
        new_job_application.email,
        "Acknowledgement",
        "We have received your job application"
    )
    #background_tasks.add_task(evaluate_resume, resume_contents, job_post.description, new_job_application.id)

    background_tasks.add_task(ingest_resume_for_recommendataions, resume_contents, 
                            file_url, new_job_application.id, vector_store)
    return new_job_application
    
class AdminLoginForm(BaseModel):
   username : str
   password : str

@app.post("/api/admin-login")
async def admin_login(response: Response, admin_login_form: Annotated[AdminLoginForm, Form()]):
   auth_response = authenticate_admin(admin_login_form.username, admin_login_form.password)
   if auth_response is not None:
      secure = settings.PRODUCTION
      response.set_cookie(key="admin_session", value=auth_response, httponly=True, secure=secure, samesite="Lax")
      return {}
   else:
      raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
   
@app.get("/api/me")
async def me(req: Request):
    return {"is_admin": req.state.is_admin}
   
@app.post("/api/admin-logout")
async def admin_login(request: Request, response: Response) :
    delete_admin_session(request.cookies.get("admin_session"))
    secure = settings.PRODUCTION
    response.delete_cookie(key="admin_session",
        httponly=True, secure=secure,
        samesite="Lax")
    return {}

class JobPostForm(BaseModel):
   title : str
   description: str
   job_board_id : int

@app.post("/api/job-posts")
async def api_create_job_post(job_post_form: Annotated[JobPostForm, Form()], db: Session = Depends(get_db_session)):
   jobBoard = db.get(JobBoard, job_post_form.job_board_id)
   if not jobBoard:
      raise HTTPException(status_code=400)
   jobPost = JobPost(title=job_post_form.title, 
                     description=job_post_form.description, 
                     job_board_id = job_post_form.job_board_id)
   db.add(jobPost)
   db.commit()
   db.refresh(jobPost)
   return jobPost

class JobDescriptionForm(BaseModel):
    description: str

@app.post("/api/review-job-description")
async def api_create_job_post(job_post_form: Annotated[JobDescriptionForm, Form()]):
   reviewed_application = review_application(job_post_form.description)
   return reviewed_application

@app.get("/api/job-posts/{job_post_id}/recommend")
async def api_recommend_resume(
   job_post_id, 
   db: Session = Depends(get_db_session),
   vector_store = Depends(get_vector_store)):
   
   job_post = db.get(JobPost, job_post_id)
   if not job_post:
      raise HTTPException(status_code=400)
   job_description = job_post.description
   recommended_resume = get_recommendation(job_description, vector_store)   
   application_id = recommended_resume.metadata["_id"]
   job_application = db.get(JobApplication, application_id)
   return job_application

# @app.post("/add")
# async def add(data: Dict[str, int]):
#   result = data["x"] + data["y"]
#   return {
#     "result": result
#   }

# @app.get("/add/")
# async def add(x: int = 0, y: int = 0):
#   return {"result": x+y}

jobBoards = {
    "acme": [
        {
            "img": "shopify.jpg",
            "alt": "ACME",
            "title": "Customer Support Executive",
            "jobDescription": "The Customer Support Executive is responsible for maximizing customer satisfaction by handling inquiries, resolving issues, and providing guidance related to products and services. Through prompt and courteous communication, the role enhances the overall customer experience and contributes to building long-term customer relationships."
        },
        {
            "title": "Project Manager",
            "jobDescription": "The Project Manager is responsible for planning, executing, and delivering projects within defined scope, timelines, and budget. By coordinating cross-functional teams, managing risks, and ensuring effective communication with stakeholders, the Project Manager ensures successful project outcomes and drives operational excellence."
        }
    ],
    "bcg": [
        {
            "img": "shopify.jpg",
            "alt": "BCG",
            "title": "Technical Architect",
            "jobDescription": "The Technical Architect is responsible for designing and overseeing the technical architecture of systems and solutions. By providing technical leadership, ensuring alignment with business requirements, and guiding development teams, the architect delivers scalable, secure, and high-quality technology solutions that support organizational goals."
        },
        {
            "title": "Junior Software Developer",
            "jobDescription": "The Junior Software Developer supports the development and maintenance of software applications under the guidance of senior engineers. This role involves writing clean code, fixing bugs, performing tests, and learning best practices to contribute to building reliable and efficient software solutions."
        }
    ],
    "atlas": [
        {
            "img": "shopify.jpg",
            "alt": "ATLAS",
            "title": "Technical Architect",
            "jobDescription": "The Technical Architect is responsible for designing and overseeing the technical architecture of systems and solutions. By providing technical leadership, ensuring alignment with business requirements, and guiding development teams, the architect delivers scalable, secure, and high-quality technology solutions that support organizational goals."
        },
        {
            "title": "Junior Software Developer",
            "jobDescription": "The Junior Software Developer supports the development and maintenance of software applications under the guidance of senior engineers. This role involves writing clean code, fixing bugs, performing tests, and learning best practices to contribute to building reliable and efficient software solutions."
        }
    ]
}
  
#   Cartesian Join vs Inner Join

# @app.get("/api/job-boards/{slug}")
# async def api_company_job_board(slug):
#   with get_db_session() as session:
#      jobPosts = session.query(JobPost).filter(JobBoard.slug.__eq__(slug)).all()
#      return jobPosts
  
@app.get("/api/job-boards/{slug}")
async def api_company_job_board(slug):
  with get_db_session() as session:
     jobPosts = session.query(JobPost) \
        .join(JobPost.job_board) \
        .filter(JobBoard.slug.__eq__(slug)) \
        .all()
     return jobPosts


@app.get("/job-boards/{slug}")
async def company_job_board(request: Request, slug : str):
#  if slug not in jobBoards:
#         raise HTTPException(status_code=404, detail="Item not found")
 job_board = jobBoards[slug]
 return templates.TemplateResponse(
        request=request, name="job-board.html", context={"job_board": job_board}
    )

@app.get("/api/job-boards/{slug}")
async def company_job_board(request: Request, slug : str):
#  if slug not in jobBoards:
#         raise HTTPException(status_code=404, detail="Item not found")
 job_board = jobBoards[slug]
 return job_board

# class Job(BaseModel):
#     id: int
#     title: str
#     department: str
#     manager: str
#     location: str
#     open: str
#     close: str
#     status: str

# # メモリ上に求人情報を保存するためのリスト
# jobs: List[Job] = []

# @app.post("/jobs", response_model=Job)
# async def create_job(job: Job):
#     jobs.append(job)
#     return job

# @app.get("/jobs", response_model=List[Job])
# async def get_jobs():
#     return jobs

@app.get("/{full_path:path}")
async def catch_all(full_path: str):
  indexFilePath = os.path.join("frontend", "build", "client", "index.html")
  return FileResponse(path=indexFilePath, media_type="text/html")