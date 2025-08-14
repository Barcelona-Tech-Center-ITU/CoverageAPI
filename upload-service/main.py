from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from shared import (
    get_db,
    db_manager,
    validate_api_key,
    setup_logging,
    ServiceSettings
)


SERVICE_NAME = "upload-service"
service_settings = ServiceSettings(
    service_name=SERVICE_NAME,
    service_description="GIGA Coverage API Upload Speed Testing Service"
)

logger = setup_logging(service_settings.service_name)

app = FastAPI(
    title="GIGA Coverage Upload Service",
    version=service_settings.service_version
)
db_manager.create_tables()


class UploadTestResponse(BaseModel):
    status: str
    message: str
    file_size_bytes: int


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
        is_all_file_read = False
        while not is_all_file_read:
            chunk = await file.read(8192)  # 8KB chunks
            if not chunk:
                is_all_file_read = True
            total_bytes += len(chunk)
            # Data is discarded - not stored anywhere

        logger.info(
            f"Upload test completed for phone {phone_identifier[:8]}...: received {total_bytes} bytes"
        )

        return UploadTestResponse(
            status="success",
            message="Upload test completed successfully",
            file_size_bytes=total_bytes
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during upload test: {e}")
        raise HTTPException(
            status_code=500,
            detail="Upload test failed",
        )


@app.get("/health")
async def health_check():
    """Health check endpoint for load balancer"""
    return {
        "status": "healthy",
        "service": SERVICE_NAME,
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": f"GIGA Coverage - {service_settings.service_description}",
        "version": service_settings.service_version
    }
