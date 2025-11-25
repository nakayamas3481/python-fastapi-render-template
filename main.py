import os
from typing import Annotated, List
from fastapi import Body, FastAPI, File, Form, Request, HTTPException, UploadFile
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field, field_validator
from config import settings
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from db import get_db_session
from models import JobBoard
from models import JobPost
from file_storage import upload_file

app = FastAPI()

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
async def api_create_new_job_board(job_board_form: Annotated[JobBoardForm, Form()]):
    logo_contents = await job_board_form.logo.read()
    file_url = upload_file("company-logos", \
                           job_board_form.logo.filename, \
                           logo_contents, \
                           job_board_form.logo.content_type)
    with get_db_session() as session:
        new_job_board = JobBoard(slug=job_board_form.slug, logo_url=file_url)
        session.add(new_job_board)
        session.commit()
        session.refresh(new_job_board)
        return new_job_board

@app.get("/api/job-boards/{job_board_id}/job-posts")
async def api_company_job_board(job_board_id):
  with get_db_session() as session:
     jobPosts = session.query(JobPost).filter(JobPost.job_board_id.__eq__(job_board_id)).all()
     return jobPosts

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