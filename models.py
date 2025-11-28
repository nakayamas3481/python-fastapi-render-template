from sqlalchemy import Column, Date, ForeignKey, Integer, String
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB

Base = declarative_base()

class JobBoard(Base):
  __tablename__ = 'job_boards'
  id = Column(Integer, primary_key=True)
  slug = Column(String, nullable=False, unique=True)
  logo_url = Column(String, nullable=True)

class JobPost(Base):
  __tablename__ = 'job_posts'
  id = Column(Integer, primary_key=True)
  title = Column(String, nullable=False)
  description = Column(String, nullable=False)
  job_board_id = Column(Integer, ForeignKey("job_boards.id"),  nullable=False)
  job_board = relationship("JobBoard")
  close_date = Column(Date, nullable=True)
 
class JobApplication(Base):
  __tablename__ = 'job_applications'
  id = Column(Integer, primary_key=True)
  firtst_name = Column(String, nullable=False)
  last_name = Column(String, nullable=False)
  email = Column(String, nullable=False)
  resume_url = Column(String, nullable=True)
  job_post_id = Column(Integer, ForeignKey("job_posts.id"),  nullable=False)
  job_post = relationship("JobPost")
  
class JobApplicationAIEvaluation(Base):
  __tablename__ = 'job_application_ai_evaluations'
  id = Column(Integer, primary_key=True)
  job_application_id = Column(Integer, ForeignKey("job_applications.id"), nullable=False)
  overall_score = Column(Integer, nullable=False)
  evaluation = Column(JSONB, nullable=False) 