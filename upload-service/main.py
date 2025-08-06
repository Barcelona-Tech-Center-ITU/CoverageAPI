from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import time
import logging
import asyncio
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="GIGA Coverage Upload Service", version="1.0.0")

# Database configuration for API key validation
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
    created_at = Column(DateTime)

class UploadTestResponse(BaseModel):
    status: str
    message: str
    file_size_bytes: int

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def validate_api_key(api_key: str, db: Session) -> str:
    """
    Validate API key against stored keys.
    Raises HTTPException if key is invalid.
    """
    api_key_record = db.query(ApiKey).filter(ApiKey.api_key == api_key).first()
    if not api_key_record:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return api_key_record.phone_identifier

@app.post("/api/test-data-upload", response_model=UploadTestResponse)
async def test_data_upload(
    api_key: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Accept file upload for speed testing purposes.
    Validates API key and consumes uploaded data without storing it.
    The client library calculates upload speed based on timing.
    """
    try:
        if not api_key:
            raise HTTPException(status_code=400, detail="API key is required")
        
        if not file:
            raise HTTPException(status_code=400, detail="File is required")
        
        # Validate API key
        phone_identifier = await validate_api_key(api_key, db)
        
        # Read and discard the uploaded file data
        total_bytes = 0
        while True:
            chunk = await file.read(8192)  # 8KB chunks
            if not chunk:
                break
            total_bytes += len(chunk)
            # Data is discarded - not stored anywhere
        
        logger.info(f"Upload test completed for phone {phone_identifier[:8]}...: received {total_bytes} bytes")
        
        return UploadTestResponse(
            status="success",
            message="Upload test completed successfully",
            file_size_bytes=total_bytes
        )
    
    except HTTPException:
        # Re-raise HTTP exceptions (like invalid API key)
        raise
    except Exception as e:
        logger.error(f"Error during upload test: {e}")
        raise HTTPException(status_code=500, detail="Upload test failed")

@app.get("/health")
async def health_check():
    """Health check endpoint for load balancer"""
    return {"status": "healthy", "service": "upload-service"}

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "GIGA Coverage Upload Service", "version": "1.0.0"}

@app.get("/upload-info")
async def upload_info():
    """Information about upload testing capabilities"""
    return {
        "service": "upload-service",
        "max_file_size": "100MB",
        "supported_formats": "any",
        "chunk_size": "8KB",
        "purpose": "Accept uploads for client-side speed calculation"
    }