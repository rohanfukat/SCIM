from fastapi import FastAPI, Depends
from typing import List
import datetime, os
from sqlmodel import create_engine,Session
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()
DATABASE_URL = os.getenv("DATABASE_URL")

# Dependency to get database session
def get_session():
    engine = create_engine(DATABASE_URL)
    with Session(engine) as session:
        yield session


