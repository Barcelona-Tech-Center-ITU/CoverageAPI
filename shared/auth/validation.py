from typing import Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session
from ..database.models import ApiKey


async def validate_api_key(api_key: Optional[str], db: Session) -> str:
    """
    Validate API key against stored keys and return phone_identifier.

    Args:
        api_key: The API key to validate
        db: Database session

    Returns:
        phone_identifier: The phone identifier associated with the API key

    Raises:
        HTTPException: If the API key is invalid (401 status)
    """
    if not api_key:
        raise HTTPException(status_code=400, detail="API key is required")

    api_key_record = db.query(ApiKey).filter(ApiKey.api_key == api_key).first()
    if not api_key_record:
        raise HTTPException(status_code=401, detail="Invalid API key")

    return api_key_record.phone_identifier
