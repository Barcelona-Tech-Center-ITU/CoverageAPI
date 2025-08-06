from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
import uuid
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="GIGA Coverage Key Service", version="1.0.0")

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://coverage:coverage@postgres:5432/coverage_db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models
class ApiKey(Base):
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    phone_identifier = Column(String, unique=True, index=True, nullable=False)
    api_key = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# Pydantic models
class GenerateKeyRequest(BaseModel):
    phone_identifier: str

class GenerateKeyResponse(BaseModel):
    api_key: str
    status: str

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create tables
Base.metadata.create_all(bind=engine)

@app.post("/api/generate-key", response_model=GenerateKeyResponse)
async def generate_api_key(request: GenerateKeyRequest, db: Session = Depends(get_db)):
    """
    Generate and store an API key for a device based on phone_identifier.
    Links the phone_identifier to a unique API key for identification and privacy.
    """
    try:
        if not request.phone_identifier:
            raise HTTPException(status_code=400, detail="Phone identifier is required")
        
        # Check if this phone_identifier already has an API key
        existing_key = db.query(ApiKey).filter(ApiKey.phone_identifier == request.phone_identifier).first()
        
        if existing_key:
            logger.info(f"Returning existing API key for phone: {request.phone_identifier[:8]}...")
            return GenerateKeyResponse(
                api_key=existing_key.api_key,
                status="success"
            )
        
        # Generate new UUID-based API key
        api_key = str(uuid.uuid4())
        
        # Store in database
        new_api_key = ApiKey(
            phone_identifier=request.phone_identifier,
            api_key=api_key
        )
        
        db.add(new_api_key)
        db.commit()
        db.refresh(new_api_key)
        
        logger.info(f"Generated new API key for phone: {request.phone_identifier[:8]}...")
        
        return GenerateKeyResponse(
            api_key=api_key,
            status="success"
        )
    
    except Exception as e:
        logger.error(f"Error generating API key: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to generate API key")

@app.get("/health")
async def health_check():
    """Health check endpoint for load balancer"""
    return {"status": "healthy", "service": "key-service"}

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "GIGA Coverage Key Service", "version": "1.0.0"}