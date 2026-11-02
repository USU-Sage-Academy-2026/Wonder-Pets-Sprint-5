import os
from dotenv import load_dotenv
from supabase import create_client

# Loads the .env file
load_dotenv()

# Get the database credentials
url = os.getenv("SUPABASE_URL")
secret_key = os.getenv("SUPABASE_SECRET_KEY")

# Create the Supabase connection
supabase = create_client("https://ffsepgplvhwpiopwuocv.supabase.co", "https://ffsepgplvhwpiopwuocv.supabase.co")

