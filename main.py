# main.py
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
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
            "id": user['id'],
            "name": user['full_name'],
            "email": user['email'],
            "role": user['role']
        }
        
        # If student, get additional info
        if user_role == 'student':
            try:
                student_response = supabase_admin.table('students')\
                    .select('roll_number, class_id')\
                    .eq('user_id', user['id'])\
                    .execute()
                if student_response.data:
                    student_data = student_response.data[0]
                    user_data['roll_number'] = student_data.get('roll_number')
                    user_data['class_id'] = student_data.get('class_id')
            except Exception as e:
                logger.warning(f"Could not fetch student data: {str(e)}")
        
        # If teacher, get additional info
        elif user_role == 'teacher':
            try:
                teacher_response = supabase_admin.table('teachers')\
                    .select('employee_id, department')\
                    .eq('user_id', user['id'])\
                    .execute()
                if teacher_response.data:
                    teacher_data = teacher_response.data[0]
                    user_data['employee_id'] = teacher_data.get('employee_id')
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

@app.get("/api/student/{student_id}/dashboard")
def get_student_dashboard(student_id: int):
    """Get student dashboard data"""
    try:
        # Get student with joined data using admin client
        student_response = supabase_admin.table('students')\
            .select('*, classes(name), users(full_name)')\
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
            "roll_number": student.get('roll_number', 'Unknown'),
            "class": student.get('classes', {}).get('name', 'Unknown'),
            "percentage": round(total_percentage, 2),
            "attendance": round(attendance_percentage, 2)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Dashboard error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@app.get("/api/student/{student_id}/results")
def get_student_results(student_id: int):
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
def get_student_attendance(student_id: int):
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
def get_teacher_dashboard(teacher_id: int):
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
def get_teacher_assignments(teacher_id: int):
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