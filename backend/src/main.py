from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import redis
from .routes import student
from .database.connection import connect_to_mongo, close_mongo_connection
from .utils.backup_service import backup_service

# Initialize Redis connection for rate limiting
redis_client = redis.Redis(host="redis", port=6379, db=0, decode_responses=True)

# Initialize rate limiter with Redis storage
limiter = Limiter(key_func=get_remote_address, storage_uri="redis://redis:6379")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_to_mongo()
    # Start backup service after successful MongoDB connection
    backup_service.start_scheduler()
    print("🚀 Backup service initialized and scheduled")
    yield
    # Shutdown
    await close_mongo_connection()


app = FastAPI(
    title="The Turing Test 25 Registration API", version="1.0.0", lifespan=lifespan
)

# Add rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

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
@limiter.limit("10/minute")
async def root(request: Request):
    return {"message": "The Turing Test 25 Registration API"}


@app.get("/health")
@limiter.limit("30/minute")
async def health_check(request: Request):
    return {"status": "healthy"}
