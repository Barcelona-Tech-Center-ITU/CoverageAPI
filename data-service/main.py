from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from shared import (
    get_db,
    db_manager,
    CoverageMeasurement,
    validate_api_key,
    setup_logging,
    ServiceSettings
)
SERVICE_NAME = "data-service"
service_settings = ServiceSettings(
    service_name=SERVICE_NAME,
    service_description="GIGA Coverage Data Collection Service"
)
logger = setup_logging(service_settings.service_name)

app = FastAPI(
    title="GIGA Coverage Data Service",
    version=service_settings.service_version
)
db_manager.create_tables()


class SendDataRequest(BaseModel):
    api_key: str
    latitude: float = None
    longitude: float = None
    gps_accuracy: float = None
    signal_strength_dbm: int = None
    signal_strength_asu: int = None
    network_type: str = None
    data_network_type: str = None
    mobile_country_code: int = None
    network_code: int = None
    cell_id: int = None
    app_name: str = None
    app_version: str = None
    library_version: str = None
    download_speed: float = None
    upload_speed: float = None
    timestamp: str = None


class SendDataResponse(BaseModel):
    status: str
    message: str


@app.post("/api/send-data", response_model=SendDataResponse)
async def send_coverage_data(request: SendDataRequest, db: Session = Depends(get_db)):
    """
    Store coverage measurement data in the database.
    Validates API key against stored keys before accepting data.
    """
    try:
        if not request.api_key:
            raise HTTPException(status_code=400, detail="API key is required")

        phone_identifier = await validate_api_key(request.api_key, db)
        measurement = CoverageMeasurement(
            api_key=request.api_key,
            phone_identifier=phone_identifier,
            latitude=request.latitude,
            longitude=request.longitude,
            gps_accuracy=request.gps_accuracy,
            signal_strength_dbm=request.signal_strength_dbm,
            signal_strength_asu=request.signal_strength_asu,
            network_type=request.network_type,
            data_network_type=request.data_network_type,
            mcc=request.mobile_country_code,
            mnc=request.network_code,
            cell_id=request.cell_id,
            app_name=request.app_name,
            app_version=request.app_version,
            library_version=request.library_version,
            download_speed_kbps=request.download_speed,
            upload_speed_kbps=request.upload_speed,
            timestamp=request.timestamp
        )

        db.add(measurement)
        db.commit()
        db.refresh(measurement)

        logger.info(
            f"Stored measurement for phone: {phone_identifier[:8]}... (ID: {measurement.id})")

        return SendDataResponse(
            status="success",
            message="Coverage data stored successfully"
        )

    except Exception as e:
        logger.error(f"Error storing coverage data: {e}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to store coverage data"
        )


@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint with database connectivity test"""
    try:
        # Test database connection
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "service": SERVICE_NAME,
            "database": "connected",
        }
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            "status": "unhealthy",
            "service": SERVICE_NAME,
            "database": "disconnected",
        }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": f"GIGA Coverage - {service_settings.service_description}",
        "version": service_settings.service_version
    }
