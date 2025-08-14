from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr, Field
from datetime import date
import shutil
import os

# ------------------- Setup -------------------
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = FastAPI(
    title="Student API",
    description="API for student records and file uploads",
    version="1.0"
)

# Serve uploaded files
app.mount("/static", StaticFiles(directory=UPLOAD_FOLDER), name="static")

# ------------------- Models -------------------
class User(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=15)
class UpdateUser(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=15)


class Student(BaseModel):
    name: str = Field(..., )
    degree: str = Field(...,)
    DOB: date = Field(..., example="2000-05-15")
    CNIC: str = Field(
        ...,
        min_length=13,
        max_length=13,
        example="3520212345678",
        description="13-digit CNIC number without dashes"
    )

# ------------------- Memory Storage -------------------
users = []      # List of registered users
students = []   # List of student records

# ------------------- Routes -------------------
@app.get("/", summary="Welcome message")
def root():
    return {
        "message": "Welcome to Student API",
        "status": "ok"
    }

@app.post("/signup", summary="Register a new user")
def signup(user: User):
    # Check if user already exists
    if any(u.email == user.email for u in users):
        return {
            "message": "User already exists",
            "status": "error"
        }
    try:
        users.append(user)
        return {
            "message": "User registered successfully",
            "status": "ok",
            "user": user.dict()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/update", summary="Update an existing user's password")
def update_user(user_update: UpdateUser):
    try:
        # Search for the user in the users list
        for user in users:
            if user.email == user_update.email:
                user.password = user_update.password
                return {
                    "message": "User password updated successfully",
                    "status": "ok",
                    "user": user.dict()
                }

        # If user not found
        return {
            "message": "User not found",
            "status": "error"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating user: {str(e)}")


@app.post("/student", summary="Create a new student record")
def create_student(student: Student, email: EmailStr):
    # Ensure the email belongs to a signed-up user
    if not any(u.email == email for u in users):
        return {
            "message": "User not signed up. Please sign up first.",
            "status": "error"
        }
    try:
        students.append(student)
        return {
            "message": "Student record created successfully",
            "status": "ok",
            "student": student.dict()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload", summary="Upload a file")
async def upload_file(file: UploadFile = File(...)):
    try:
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        file_url = f"/static/{file.filename}"
        return {
            "message": "File uploaded successfully",
            "status": "ok",
            "filename": file.filename,
            "file_url": file_url
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")
