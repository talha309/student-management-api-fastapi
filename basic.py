from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr, Field
from datetime import date
from typing import List
import shutil
import os

# Configuration
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize FastAPI app
app = FastAPI(
    title="Student Management API",
    description="API for managing student records and file uploads",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Mount static files directory
app.mount("/static", StaticFiles(directory=UPLOAD_FOLDER), name="static")

# Pydantic Models
class User(BaseModel):
    email: EmailStr
    password: str = Field(
        ...,
        min_length=6,
        max_length=15,
        description="Password must be 6-15 characters long"
    )

class Student(BaseModel):
    name: str = Field(
        ...,
        example="Ali Khan",
        description="Full name of the student"
    )
    degree: str = Field(
        ...,
        example="BS Computer Science",
        description="Degree program of the student"
    )
    DOB: date = Field(
        ...,
        example="2000-05-15",
        description="Date of Birth in YYYY-MM-DD format"
    )
    CNIC: str = Field(
        ...,
        min_length=13,
        max_length=13,
        example="3520212345678",
        description="13-digit CNIC number without dashes"
    )

# In-memory storage (for demonstration; use a database in production)
users: List[User] = []
students: List[Student] = []

@app.get(
    "/",
    summary="Welcome endpoint",
    description="Returns a welcome message for the Student API"
)
async def root():
    return {
        "message": "Welcome to Student Management API",
        "status": "ok",
        "version": app.version
    }

@app.post(
    "/signup",
    summary="User signup",
    description="Register a new user with email and password"
)
async def signup(user: User):
    # Check if user already exists
    if any(existing_user.email == user.email for existing_user in users):
        raise HTTPException(
            status_code=400,
            detail="User with this email already exists"
        )
    
    try:
        users.append(user)
        return {
            "message": "User registered successfully",
            "status": "ok",
            "user": {
                "email": user.email,
                "created_at": date.today().isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Registration failed: {str(e)}"
        )

@app.post(
    "/student",
    summary="Create student record",
    description="Add a new student record (requires user signup)"
)
async def create_student(student: Student, email: str = None):
    # Basic user check (in production, implement proper authentication)
    if not any(user.email == email for user in users):
        raise HTTPException(
            status_code=401,
            detail="User not registered. Please signup first"
        )
    
    try:
        students.append(student)
        return {
            "message": "Student record created successfully",
            "status": "ok",
            "student": student.dict()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create student record: {str(e)}"
        )

@app.post(
    "/upload",
    summary="Upload a file",
    description="Upload a file to the server and get its URL"
)
async def upload_file(file: UploadFile = File(...)):
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(
                status_code=400,
                detail="No file provided"
            )
            
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        
        # Check for file existence
        if os.path.exists(file_path):
            raise HTTPException(
                status_code=400,
                detail="File with this name already exists"
            )

        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        file_url = f"/static/{file.filename}"
        return {
            "message": "File uploaded successfully",
            "status": "ok",
            "filename": file.filename,
            "file_url": file_url,
            "uploaded_at": date.today().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"File upload failed: {str(e)}"
        )
    finally:
        await file.close()

# Optional: Add endpoint to list all students
@app.get(
    "/students",
    summary="List all students",
    description="Retrieve all student records",
    response_model=List[Student]
)
async def get_students():
    return students