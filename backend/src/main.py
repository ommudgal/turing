from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import student
from .database.connection import connect_to_mongo, close_mongo_connection


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_to_mongo()
    yield
    # Shutdown
    await close_mongo_connection()


app = FastAPI(
    title="Trained & Tuned'25 Registration API", version="1.0.0", lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://frontend:80"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(student.router, prefix="/api/v1/student", tags=["student"])


@app.get("/")
async def root():
    return {"message": "Trained & Tuned'25 Registration API"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
