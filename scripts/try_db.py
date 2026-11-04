import sys
from pathlib import Path
from getpass import getpass
from dotenv import load_dotenv

# Find the main project folder
project_folder = Path(__file__).resolve().parent.parent

# Add the main folder to Python's search path
sys.path.insert(0, str(project_folder))

# Load environment variables
load_dotenv(project_folder / ".env")

# Import our function from db.py
from db import login_customer, url

# Check that the database URL loaded
print(url is not None)
