# main.py
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from pydantic import BaseModel
from datetime import date
import logging
from supabase_client import supabase, supabase_admin

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# CORS middleware - Updated with your frontend ports
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:8080",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "https://aryan-school-management-frontend.vercel.app",  # ← ADD THIS
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- PYDANTIC MODELS ----------

class LoginRequest(BaseModel):
    email: str
    password: str

class AssignmentResponse(BaseModel):
    id: int
    title: str
    description: str
    subject_name: str
    due_date: date
    total_marks: int
    file_url: str
    status: str

# ---------- API ENDPOINTS ----------

@app.get("/")
def root():
    return {"message": "College Management API is running!"}

@app.post("/api/login")
def login(request: LoginRequest):
    """Authenticate user using Supabase"""
    try:
        logger.info(f"Login attempt for email: {request.email}")
        
        # Use admin client to bypass RLS
        response = supabase_admin.table('users').select('*').eq('email', request.email).execute()
        
        if not response.data:
            logger.warning(f"Login failed - user not found: {request.email}")
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        user = response.data[0]
        
        # Check password (in production, use proper hashing)
        if user['password'] != request.password:
            logger.warning(f"Login failed - wrong password: {request.email}")
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Get role-specific data (if needed)
        user_role = user.get('role', '').lower()
        user_data = {
            "id": user['id'],  # This is a UUID string
            "name": user['full_name'],
            "email": user['email'],
            "role": user['role']
        }
        
        # If student, get additional info
        if user_role == 'student':
            try:
                # Use the 'id' column instead of 'student_id'
                # The 'id' column in students table matches the user's UUID
                student_response = supabase_admin.table('students')\
                    .select('*')\
                    .eq('id', user['id'])\
                    .execute()
                if student_response.data:
                    student_data = student_response.data[0]
                    user_data['student_id'] = student_data.get('id')
                    user_data['roll_no'] = student_data.get('roll_no', 'N/A')
                    user_data['phone'] = student_data.get('phone_number', '')
                    user_data['address'] = student_data.get('address', '')
                    user_data['faculty'] = student_data.get('faculty', '')
                    user_data['student_record'] = student_data
                    logger.info(f"Found student record for user: {user['id']}")
                else:
                    logger.warning(f"No student record found for user: {user['id']}")
                    user_data['roll_no'] = 'N/A'
            except Exception as e:
                logger.warning(f"Could not fetch student data: {str(e)}")
                user_data['roll_no'] = 'N/A'
        
        # If teacher, get additional info
        elif user_role == 'teacher':
            try:
                teacher_response = supabase_admin.table('teachers')\
                    .select('*')\
                    .eq('teacher_id', user['id'])\
                    .execute()
                if teacher_response.data:
                    teacher_data = teacher_response.data[0]
                    user_data['teacher_id'] = teacher_data.get('id')
                    user_data['employee_id'] = teacher_data.get('employee_id', 'N/A')
                    user_data['department'] = teacher_data.get('department')
            except Exception as e:
                logger.warning(f"Could not fetch teacher data: {str(e)}")
        
        logger.info(f"Login successful for: {request.email} with role: {user_role}")
        return {
            "success": True,
            "user": user_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@app.get("/api/user/{user_id}/profile")
def get_user_profile(user_id: str):
    """Get user profile data with role-specific information"""
    try:
        logger.info(f"Fetching profile for user: {user_id}")
        
        # Get user data
        user_response = supabase_admin.table('users').select('*').eq('id', user_id).execute()
        
        if not user_response.data:
            logger.warning(f"User not found: {user_id}")
            raise HTTPException(status_code=404, detail="User not found")
        
        user = user_response.data[0]
        user_role = user.get('role', '').lower()
        
        profile_data = {
            "id": user['id'],
            "full_name": user['full_name'],
            "email": user['email'],
            "role": user['role'],
            "profile_pic": None,
            "phone": None,
            "address": None,
            "additional_info": {}
        }
        
        # Get role-specific data
        if user_role == 'student':
            try:
                # Use the 'id' column instead of 'student_id'
                student_response = supabase_admin.table('students')\
                    .select('*')\
                    .eq('id', user_id)\
                    .execute()
                if student_response.data:
                    student = student_response.data[0]
                    profile_data["profile_pic"] = student.get('profile_pic')
                    profile_data["phone"] = student.get('phone_number')
                    profile_data["address"] = student.get('address')
                    
                    profile_data["additional_info"] = {
                        "roll_no": student.get('roll_no', 'N/A'),
                        "faculty": student.get('faculty', ''),
                        "email": student.get('email', ''),
                        "full_name": student.get('full_name', ''),
                        "student_id": student.get('student_id', '')  # This is STU-2024-009
                    }
                    logger.info(f"Student profile data fetched for user: {user_id}")
                else:
                    logger.warning(f"No student record found for user: {user_id}")
                    profile_data["additional_info"] = {"roll_no": "N/A"}
            except Exception as e:
                logger.error(f"Error fetching student profile: {str(e)}")
                profile_data["additional_info"] = {"roll_no": "N/A"}
                
        elif user_role == 'teacher':
            try:
                teacher_response = supabase_admin.table('teachers')\
                    .select('*')\
                    .eq('teacher_id', user_id)\
                    .execute()
                if teacher_response.data:
                    teacher = teacher_response.data[0]
                    profile_data["profile_pic"] = teacher.get('profile_pic')
                    profile_data["phone"] = teacher.get('phone')
                    profile_data["additional_info"] = {
                        "employee_id": teacher.get('employee_id', 'N/A'),
                        "department": teacher.get('department')
                    }
                    logger.info(f"Teacher profile data fetched for user: {user_id}")
                else:
                    logger.warning(f"No teacher record found for user: {user_id}")
            except Exception as e:
                logger.error(f"Error fetching teacher profile: {str(e)}")
        
        return profile_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Profile error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@app.get("/api/student/{student_id}/dashboard")
def get_student_dashboard(student_id: str):
    """Get student dashboard data"""
    try:
        # Get student with joined data using admin client
        student_response = supabase_admin.table('students')\
            .select('*, users(full_name)')\
            .eq('id', student_id)\
            .execute()
        
        if not student_response.data:
            raise HTTPException(status_code=404, detail="Student not found")
        
        student = student_response.data[0]
        
        # Get results
        results_response = supabase_admin.table('results')\
            .select('*, subjects(name)')\
            .eq('student_id', student_id)\
            .execute()
        results = results_response.data
        
        total_percentage = sum(r['percentage'] for r in results) / len(results) if results else 0
        
        # Get attendance
        attendance_response = supabase_admin.table('attendance')\
            .select('*')\
            .eq('student_id', student_id)\
            .execute()
        attendance = attendance_response.data
        present = sum(1 for a in attendance if a['status'] == 'present')
        total = len(attendance)
        attendance_percentage = (present / total * 100) if total > 0 else 0
        
        return {
            "name": student.get('users', {}).get('full_name', 'Unknown'),
            "roll_no": student.get('roll_no', 'N/A'),
            "faculty": student.get('faculty', 'Unknown'),
            "percentage": round(total_percentage, 2),
            "attendance": round(attendance_percentage, 2)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Dashboard error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@app.get("/api/student/{student_id}/results")
def get_student_results(student_id: str):
    """Get student results"""
    try:
        response = supabase_admin.table('results')\
            .select('*, subjects(name)')\
            .eq('student_id', student_id)\
            .execute()
        results = response.data
        
        result_list = []
        for r in results:
            result_list.append({
                "subject": r.get('subjects', {}).get('name', 'Unknown'),
                "marks_obtained": r.get('marks_obtained', 0),
                "total_marks": r.get('total_marks', 0),
                "grade": r.get('grade', 'N/A'),
                "percentage": round(r.get('percentage', 0), 2)
            })
        
        return result_list
    except Exception as e:
        logger.error(f"Results error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@app.get("/api/student/{student_id}/attendance")
def get_student_attendance(student_id: str):
    """Get student attendance"""
    try:
        response = supabase_admin.table('attendance')\
            .select('*, subjects(name)')\
            .eq('student_id', student_id)\
            .order('date', desc=True)\
            .limit(10)\
            .execute()
        attendance_records = response.data
        
        attendance_list = []
        for a in attendance_records:
            attendance_list.append({
                "date": a.get('date'),
                "status": a.get('status'),
                "subject": a.get('subjects', {}).get('name', 'Unknown')
            })
        
        return attendance_list
    except Exception as e:
        logger.error(f"Attendance error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@app.get("/api/teacher/{teacher_id}/dashboard")
def get_teacher_dashboard(teacher_id: str):
    """Get teacher dashboard data"""
    try:
        # Get teacher details using admin client
        teacher_response = supabase_admin.table('teachers')\
            .select('*, users(full_name)')\
            .eq('id', teacher_id)\
            .execute()
        
        if not teacher_response.data:
            raise HTTPException(status_code=404, detail="Teacher not found")
        
        teacher = teacher_response.data[0]
        
        # Get subjects taught by this teacher
        subjects_response = supabase_admin.table('subjects')\
            .select('*')\
            .eq('teacher_id', teacher_id)\
            .execute()
        subjects = subjects_response.data
        subject_ids = [s['id'] for s in subjects]
        
        # Get total students (simplified)
        students_count = 0
        if subject_ids:
            # Get students from classes that have these subjects
            for subject_id in subject_ids:
                # Get class_id from subject
                subject = next((s for s in subjects if s['id'] == subject_id), None)
                if subject and subject.get('class_id'):
                    count_response = supabase_admin.table('students')\
                        .select('*', count='exact')\
                        .eq('class_id', subject['class_id'])\
                        .execute()
                    students_count += len(count_response.data)
        
        # Get pending assignments
        pending_response = supabase_admin.table('assignments')\
            .select('*', count='exact')\
            .in_('subject_id', subject_ids)\
            .execute()
        pending_assignments = len(pending_response.data) if pending_response.data else 0
        
        return {
            "name": teacher.get('users', {}).get('full_name', 'Unknown'),
            "department": teacher.get('department', 'Unknown'),
            "total_students": students_count,
            "today_classes": len(subjects),
            "pending_assignments": pending_assignments
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Teacher dashboard error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@app.get("/api/teacher/{teacher_id}/assignments")
def get_teacher_assignments(teacher_id: str):
    """Get assignments for a teacher"""
    try:
        response = supabase_admin.table('assignments')\
            .select('*, subjects(name)')\
            .eq('uploaded_by', teacher_id)\
            .execute()
        assignments = response.data
        
        assignment_list = []
        for a in assignments:
            due_date = a.get('due_date')
            today = date.today().isoformat()
            is_active = due_date and due_date >= today
            assignment_list.append({
                "id": a.get('id'),
                "title": a.get('title'),
                "description": a.get('description'),
                "subject_name": a.get('subjects', {}).get('name', 'Unknown'),
                "due_date": due_date,
                "total_marks": a.get('total_marks'),
                "file_url": a.get('file_url'),
                "status": "Active" if is_active else "Expired"
            })
        
        return assignment_list
    except Exception as e:
        logger.error(f"Assignments error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@app.get("/api/assignments")
def get_all_assignments():
    """Get all assignments (for student view)"""
    try:
        response = supabase_admin.table('assignments')\
            .select('*, subjects(name)')\
            .execute()
        assignments = response.data
        
        assignment_list = []
        for a in assignments:
            due_date = a.get('due_date')
            today = date.today().isoformat()
            is_active = due_date and due_date >= today
            assignment_list.append({
                "id": a.get('id'),
                "title": a.get('title'),
                "description": a.get('description'),
                "subject_name": a.get('subjects', {}).get('name', 'Unknown'),
                "due_date": due_date,
                "total_marks": a.get('total_marks'),
                "file_url": a.get('file_url'),
                "status": "Active" if is_active else "Expired"
            })
        
        return assignment_list
    except Exception as e:
        logger.error(f"All assignments error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@app.get("/api/health")
def health_check():
    """Health check endpoint"""
    try:
        # Test database connection using admin client
        response = supabase_admin.table('users').select('count', count='exact').execute()
        return {
            "status": "healthy",
            "database": "connected",
            "message": "API is running properly"
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)