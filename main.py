from fastapi import FastAPI, HTTPException

app = FastAPI()

@app.get("/health")
async def health():
  return {"status": "ok"}

@app.get("/")
async def root():
  return {"hello": "world"}

@app.get("/hi")
async def hi():
  return {"Hi": "Sota"}

@app.get("/add/")
async def add(x: int = 0, y: int = 0):
  return {"result": x+y}

@app.get("/multiply/")
async def multiply(x: int = 0, y: int = 0):
  return {"result": x*y}

jobBoards = {
    "acme": [
      {
        "title": "Customer Support Executive"  
      },
      {
        "title": "Project Manager"
      }
    ],
    "bcg": [
      {
         "title": "Technical Arcitect"
      },
      {
        "title": "Junior Software Developer"
      }
    ]
    # "atlas": [
    #   {
    #     "title": "Technical Arcitect",
    #     "jobDescription":"ABC"
    #   },
    #   {
    #     "title": "Junior Software Developer",
    #     "jobDescription":"DEF"
    #   }
    # ]
}

@app.get("/job-boards/{slug}")
async def company_job_board(slug : str):
#  if slug not in jobBoards:
#         raise HTTPException(status_code=404, detail="Item not found")
 return jobBoards[slug]