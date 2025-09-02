from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Shared configuration settings for all services using Pydantic validation."""

    database_url: str = Field(
        default="postgresql://coverage:coverage@postgres:5432/coverage_db",
        env="DATABASE_URL"
    )
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    service_version: str = Field(default="1.0.0", env="SERVICE_VERSION")
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=False, env="DEBUG")

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment.lower() == "production"

    @property
    def is_debug(self) -> bool:
        """Check if debug mode is enabled."""
        return self.debug

    class Config:
        env_file = ".env"
        case_sensitive = False


class ServiceSettings(Settings):
    """Service-specific settings that extend base settings."""

    service_name: str = Field(..., description="Name of the service")
    service_description: str = Field(
        default="", description="Service description")
    service_port: int = Field(default=8000, env="PORT")
    service_host: str = Field(default="0.0.0.0", env="HOST")


# Global settings instance
settings = Settings()
