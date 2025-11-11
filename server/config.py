import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Set up database configuration
    basedir = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = os.environ.get(
    'DATABASE_URI',
    f"sqlite:///{os.path.join(basedir, 'instance', 'app.db')}"
)

    SQLALCHEMY_TRACK_MODIFICATIONS = False
