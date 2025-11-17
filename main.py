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

@app.get("/add/")
async def add(x: int = 0, y: int = 0):
  return {"result": x+y}

@app.get("/multiply/")
async def multiply(x: int = 0, y: int = 0):
  return {"result": x*y}