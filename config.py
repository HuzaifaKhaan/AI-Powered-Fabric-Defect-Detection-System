# config.py

from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()
class Config:
    SECRET_KEY = os.getenv('Secret_Key')
    SQLALCHEMY_DATABASE_URI = 'postgresql://Fabrico2:password@localhost:5432/Fabrico2'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
