from fastapi import FastAPI, Depends,  HTTPException
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import os
from dotenv import load_dotenv

load_dotenv()

# Create the database URL
DATABASE_URL = os.getenv('DATABASE_URL')

# Create a SQLAlchemy engine object
engine = create_engine(DATABASE_URL)

# Create a session factory
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

# Create a base class for database models
Base = declarative_base()

# Define a database model


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    email = Column(String)


# Create the database tables
Base.metadata.create_all(bind=engine)

# Create the FastAPI app
app = FastAPI()

# Define a dependency for database sessions


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Define an endpoint that adds a new user to the database


@app.post("/users/")
def create_user(username: str, email: str, db: Session = Depends(get_db)):
    db_user = User(username=username, email=email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"id": db_user.id, "username": db_user.username, "email": db_user.email}

# Define an endpoint that lists all users


@app.get("/users/")
def list_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return [{"id": user.id, "username": user.username, "email": user.email} for user in users]


# Define an endpoint that retrieves a user by ID

@app.get("/users/{user_id}")
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return {"id": db_user.id, "username": db_user.username, "email": db_user.email}

# Define an endpoint that updates a user by ID


@app.put("/users/{user_id}")
def update_user(user_id: int, username: str, email: str, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    db_user.username = username
    db_user.email = email
    db.commit()
    db.refresh(db_user)
    return {"id": db_user.id, "username": db_user.username, "email": db_user.email}

# Define an endpoint that deletes a user by ID


@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(db_user)
    db.commit()
    return {"message": "User deleted successfully"}
