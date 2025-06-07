import os
from dotenv import load_dotenv

# Load .env file into environment variables
load_dotenv()

class Config:
    """
    Configuration class. Extend for multiple environments.
    """
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'change-this-default')
    DEBUG = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'

    # Mail (optional)
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_SENDER = os.getenv('MAIL_SENDER')
    MAIL_RECEIVER = os.getenv('MAIL_RECEIVER')

    # Snipcart public API key
    SNIPCART_API_KEY = os.getenv('SNIPCART_API_KEY')

    # Standard max content size (1MB)
    MAX_CONTENT_LENGTH = 1 * 1024 * 1024

    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    DB_PATH = os.path.join(BASE_DIR, 'admin', 'app.db')
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{DB_PATH}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY', 'supersecretkey')
    SESSION_PERMANENT = False