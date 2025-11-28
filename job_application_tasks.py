from ai_resume_evaluator import evaluate_resume_with_ai
from db import get_db_session
from models import JobApplicationAIEvaluation
from pdf_utils import extract_text_from_pdf_bytes


def evaluate_resume(resume_content, job_post_description, job_application_id):
   resume_raw_text = extract_text_from_pdf_bytes(resume_content)
   ai_evaluation = evaluate_resume_with_ai(resume_raw_text, job_post_description)
   with get_db_session() as session:
      evaluation = JobApplicationAIEvaluation(
         job_application_id = job_application_id,
         overall_score = ai_evaluation["overall_score"],
         evaluation = ai_evaluation
      )
      session.add(evaluation)
      session.commit()