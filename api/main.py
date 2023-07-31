import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import historical

app = FastAPI()
app.include_router(historical.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.environ.get("CORS_HOST", "http://localhost:3000")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Hello World"}
