from typing import List
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from config import settings
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from db import get_db_session

app = FastAPI()

app.mount("/app" , StaticFiles(directory="frontend/dist"), name = "app") 

templates = Jinja2Templates(directory="templates")

# engine = create_engine(str(settings.DATABASE_URL))
# with sessionmaker(bind=engine)() as session:
#     session.execute(text("SELECT 1"))
#     print("All good!")

@app.get("/health")
async def health():
  try:
    with get_db_session() as session:
        session.execute(text("SELECT 1"))
        return {"database": "ok"}
  except:
    return {"database": "down"}

@app.get("/")
async def root():
  return {"hello": "world"}

@app.get("/add/")
async def add(x: int = 0, y: int = 0):
  return {"result": x+y}

@app.get("/multiply/")
async def multiply(x: int = 0, y: int = 0):
  return {"result": x*y}

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

class Job(BaseModel):
    id: int
    title: str
    department: str
    manager: str
    location: str
    open: str
    close: str
    status: str

# メモリ上に求人情報を保存するためのリスト
jobs: List[Job] = []

@app.post("/jobs", response_model=Job)
async def create_job(job: Job):
    jobs.append(job)
    return job

@app.get("/jobs", response_model=List[Job])
async def get_jobs():
    return jobs