import os
from dotenv import load_dotenv

load_dotenv()

# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY = os.getenv('AZURE_OPENAI_API_KEY')
AZURE_OPENAI_ENDPOINT = os.getenv('AZURE_OPENAI_ENDPOINT', 'https://api.openai.com/v1')
AZURE_OPENAI_API_VERSION = os.getenv('AZURE_OPENAI_API_VERSION', '2024-02-01')
AZURE_OPENAI_DEPLOYMENT = os.getenv('AZURE_OPENAI_DEPLOYMENT', 'gpt-4o')

# Database Configuration
DB_SERVER = os.getenv('DB_SERVER', 'localhost')
DB_NAME = os.getenv('DB_NAME', 'SchoolDB')
DB_USERNAME = os.getenv('DB_USERNAME')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_DRIVER = 'ODBC Driver 17 for SQL Server'

# Validation function
def validate_config():
    """Validate required configuration variables"""
    errors = []
    
    if not AZURE_OPENAI_API_KEY:
        errors.append("AZURE_OPENAI_API_KEY is not set in .env file")
    
    if not DB_USERNAME:
        errors.append("DB_USERNAME is not set in .env file")
    
    if not DB_PASSWORD:
        errors.append("DB_PASSWORD is not set in .env file")
    
    return errors

def build_connection_string(server=None, database=None, username=None, password=None):
    """Build connection string with provided or default values"""
    return (
        f"DRIVER={{{DB_DRIVER}}};"
        f"SERVER={server or DB_SERVER};"
        f"DATABASE={database or DB_NAME};"
        f"UID={username or DB_USERNAME};"
        f"PWD={password or DB_PASSWORD}"
    )

CONNECTION_STRING = build_connection_string()