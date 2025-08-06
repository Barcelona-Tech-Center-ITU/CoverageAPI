from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="GIGA Coverage Data Service", version="1.0.0")

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

class CoverageMeasurement(Base):
    __tablename__ = "coverage_measurements"
    
    id = Column(Integer, primary_key=True, index=True)
    api_key = Column(String, index=True, nullable=False)
    phone_identifier = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Location data
    latitude = Column(Float)
    longitude = Column(Float)
    gps_accuracy = Column(Float)
    
    # Signal strength data
    signal_strength_dbm = Column(Integer)
    signal_strength_asu = Column(Integer)
    
    # Network information
    network_type = Column(String)
    mcc = Column(Integer)  # Mobile Country Code
    mnc = Column(Integer)  # Mobile Network Code
    cell_id = Column(BigInteger)
    
    # Device information
    app_name = Column(String)
    app_version = Column(String)
    library_version = Column(String)
    
    # Performance data
    download_speed_kbps = Column(Float)

# Pydantic models
class SendDataRequest(BaseModel):
    api_key: str
    latitude: float = None
    longitude: float = None
    gps_accuracy: float = None
    signal_strength_dbm: int = None
    signal_strength_asu: int = None
    network_type: str = None
    mcc: int = None
    mnc: int = None
    cell_id: int = None
    app_name: str = None
    app_version: str = None
    library_version: str = None
    download_speed_kbps: float = None

class SendDataResponse(BaseModel):
    status: str
    message: str

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create tables
Base.metadata.create_all(bind=engine)

async def validate_api_key(api_key: str, db: Session) -> str:
    """
    Validate API key against stored keys and return phone_identifier.
    Raises HTTPException if key is invalid.
    """
    api_key_record = db.query(ApiKey).filter(ApiKey.api_key == api_key).first()
    if not api_key_record:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return api_key_record.phone_identifier

@app.post("/api/send-data", response_model=SendDataResponse)
async def send_coverage_data(request: SendDataRequest, db: Session = Depends(get_db)):
    """
    Store coverage measurement data in the database.
    Validates API key against stored keys before accepting data.
    """
    try:
        if not request.api_key:
            raise HTTPException(status_code=400, detail="API key is required")
        
        # Validate API key and get phone_identifier
        phone_identifier = await validate_api_key(request.api_key, db)
        
        # Create new measurement record
        measurement = CoverageMeasurement(
            api_key=request.api_key,
            phone_identifier=phone_identifier,
            latitude=request.latitude,
            longitude=request.longitude,
            gps_accuracy=request.gps_accuracy,
            signal_strength_dbm=request.signal_strength_dbm,
            signal_strength_asu=request.signal_strength_asu,
            network_type=request.network_type,
            mcc=request.mcc,
            mnc=request.mnc,
            cell_id=request.cell_id,
            app_name=request.app_name,
            app_version=request.app_version,
            library_version=request.library_version,
            download_speed_kbps=request.download_speed_kbps
        )
        
        db.add(measurement)
        db.commit()
        db.refresh(measurement)
        
        logger.info(f"Stored measurement for phone: {phone_identifier[:8]}... (ID: {measurement.id})")
        
        return SendDataResponse(
            status="success",
            message="Coverage data stored successfully"
        )
    
    except HTTPException:
        # Re-raise HTTP exceptions (like invalid API key)
        raise
    except Exception as e:
        logger.error(f"Error storing coverage data: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to store coverage data")

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint with database connectivity test"""
    try:
        # Test database connection
        db.execute("SELECT 1")
        return {"status": "healthy", "service": "data-service", "database": "connected"}
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {"status": "unhealthy", "service": "data-service", "database": "disconnected"}

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "GIGA Coverage Data Service", "version": "1.0.0"}

@app.get("/stats")
async def get_stats(db: Session = Depends(get_db)):
    """Get basic statistics about stored measurements"""
    try:
        total_measurements = db.query(CoverageMeasurement).count()
        unique_devices = db.query(CoverageMeasurement.android_id).distinct().count()
        
        return {
            "total_measurements": total_measurements,
            "unique_devices": unique_devices,
            "service": "data-service"
        }
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get statistics")