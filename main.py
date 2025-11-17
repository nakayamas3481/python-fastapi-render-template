from fastapi import FastAPI

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