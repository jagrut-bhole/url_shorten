import os
from dotenv import load_dotenv
from sqlmodel import create_engine

load_dotenv()

database_url = os.getenv("DATABASE_URL", "").strip()
if not database_url:
	raise RuntimeError(
		"DATABASE_URL is empty. Set it in backend/.env before starting the app."
	)

engine = create_engine(database_url, echo=True)