import os
from dotenv import load_dotenv
import logging

# تحميل المتغيرات من ملف .env
load_dotenv()

logger = logging.getLogger(__name__)


class Config:
    """Base configuration"""
    
    # Server
    PORT = int(os.getenv('PORT', 5000))
    HOST = os.getenv('HOST', '0.0.0.0')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
    
    # Redis
    REDIS_URL = os.getenv('REDIS_URL', 'redis://default:zETnJqJUBSyOFLbKtHVdaGEAMasRaUzv@redis.railway.internal:6379')
    
    # Security
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Rate Limiting
    RATE_LIMIT = int(os.getenv('RATE_LIMIT', 100))
    RATE_LIMIT_PERIOD = int(os.getenv('RATE_LIMIT_PERIOD', 60))
    
    # Session
    SESSION_TIMEOUT = int(os.getenv('SESSION_TIMEOUT', 3600))
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        if cls.ENVIRONMENT == 'production':
            if cls.SECRET_KEY == 'dev-secret-key-change-in-production':
                logger.warning("⚠️ Using default SECRET_KEY in production! This is not secure!")
            
            if 'localhost' in cls.REDIS_URL and cls.ENVIRONMENT == 'production':
                logger.warning("⚠️ Using localhost Redis in production! Make sure REDIS_URL is set correctly!")
        
        logger.info(f"✅ Configuration loaded - Environment: {cls.ENVIRONMENT}")
        logger.info(f"📍 Server running on {cls.HOST}:{cls.PORT}")
        logger.info(f"🔗 Redis URL: {cls.REDIS_URL[:50]}...")


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    ENVIRONMENT = 'development'


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    ENVIRONMENT = 'production'


# اختيار الـ config حسب البيئة
def get_config():
    env = os.getenv('ENVIRONMENT', 'development')
    if env == 'production':
        return ProductionConfig
    return DevelopmentConfig


config = get_config()
