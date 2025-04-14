import os
from typing import List, Union, Optional, Dict, Any
from pydantic import BaseSettings, validator, AnyHttpUrl

class Settings(BaseSettings):
    # API Settings
    API_ENV: str = os.getenv("API_ENV", "development")
    API_DEBUG: bool = os.getenv("API_DEBUG", "false").lower() == "true"
    API_SECRET_KEY: str = os.getenv("API_SECRET_KEY", "insecure_key_for_dev_only")
    API_ALGORITHM: str = os.getenv("API_ALGORITHM", "HS256")
    API_ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("API_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    API_REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("API_REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    
    # Security
    ENCRYPTION_KEY: str = os.getenv("ENCRYPTION_KEY", "insecure_key_for_dev_only")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "insecure_key_for_dev_only")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    MFA_ENABLED: bool = os.getenv("MFA_ENABLED", "false").lower() == "true"
    
    # Database
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "sentinel")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "sentinel_secure_password")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "sentineldb")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    
    # Database URI
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    # Redis
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_PASSWORD: str = os.getenv("REDIS_PASSWORD", "sentinel_secure_redis")
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    
    # CORS Settings
    CORS_ORIGINS: List[str] = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")
    
    @validator("CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # ML Service
    ML_SERVICE_URL: str = os.getenv("ML_SERVICE_URL", "http://localhost:5000")
    MODEL_VERSION: str = os.getenv("MODEL_VERSION", "1.0.0")
    MODEL_UPDATE_INTERVAL: int = int(os.getenv("MODEL_UPDATE_INTERVAL", "86400"))
    ML_WORKER_THREADS: int = int(os.getenv("ML_WORKER_THREADS", "4"))
    GPU_ENABLED: bool = os.getenv("GPU_ENABLED", "true").lower() == "true"
    
    # Blockchain
    BLOCKCHAIN_NODE_URL: str = os.getenv("BLOCKCHAIN_NODE_URL", "http://localhost:7050")
    BLOCKCHAIN_API_KEY: str = os.getenv("BLOCKCHAIN_API_KEY", "insecure_key_for_dev_only")
    HYPERLEDGER_MSP_ID: str = os.getenv("HYPERLEDGER_MSP_ID", "SentinelOrgMSP")
    HYPERLEDGER_CHANNEL: str = os.getenv("HYPERLEDGER_CHANNEL", "operationschannel")
    HYPERLEDGER_CHAINCODE: str = os.getenv("HYPERLEDGER_CHAINCODE", "securityops")
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # TLS Certificates
    TLS_CERT_PATH: Optional[str] = os.getenv("TLS_CERT_PATH")
    TLS_KEY_PATH: Optional[str] = os.getenv("TLS_KEY_PATH")
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "100"))
    
    # Security Headers
    SECURITY_HEADERS: Dict[str, str] = {
        "X-Frame-Options": "DENY",
        "X-Content-Type-Options": "nosniff",
        "X-XSS-Protection": "1; mode=block",
        "Content-Security-Policy": "default-src 'self'; frame-ancestors 'none'",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Referrer-Policy": "no-referrer",
        "Cache-Control": "no-store, no-cache, must-revalidate, proxy-revalidate",
        "Pragma": "no-cache",
        "Expires": "0",
    }
    
    # System paths
    STATIC_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static")
    
    class Config:
        case_sensitive = True
        env_file = ".env"

# Create global settings object
settings = Settings() 