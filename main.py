# main.py
from fastapi import FastAPI, Depends, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from pydantic import BaseModel
from datetime import date, datetime
import logging
import json
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
        "https://aryan-school-management-frontend.vercel.app",
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

class NoteCreate(BaseModel):
    faculty: str
    semester: str
    subject: str
    topic: str
    description: Optional[str] = None
    attachments: List[str] = []

class NoteResponse(BaseModel):
    id: str
    teacher_id: str
    teacher_name: str
    faculty: str
    semester: str
    subject: str
    topic: str
    description: Optional[str] = None
    attachments: List[str]
    created_at: str

# Add these models
class AttendanceRequest(BaseModel):
    student_id: str
    subject: str
    faculty: str
    semester: str
    date: str
    status: str
    teacher_id: str

class AttendanceSubmit(BaseModel):
    attendance: List[AttendanceRequest]
    teacher_id: str

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
            "phone": user.get('phone_number'),
            "address": user.get('address'),
            "additional_info": {}
        }
        
        # Get role-specific data
        if user_role == 'student':
            try:
                student_response = supabase_admin.table('students')\
                    .select('*')\
                    .eq('id', user_id)\
                    .execute()
                if student_response.data:
                    student = student_response.data[0]
                    profile_data["profile_pic"] = student.get('profile_pic')
                    
                    if not profile_data["phone"]:
                        profile_data["phone"] = student.get('phone_number')
                    if not profile_data["address"]:
                        profile_data["address"] = student.get('address')
                    
                    profile_data["additional_info"] = {
                        "roll_no": student.get('roll_no', 'N/A'),
                        "semester": student.get('semester', 'N/A'),
                        "faculty": student.get('faculty', ''),
                        "email": student.get('email', ''),
                        "full_name": student.get('full_name', ''),
                        "student_id": student.get('student_id', '')
                    }
                    logger.info(f"Student profile data fetched for user: {user_id}")
                else:
                    logger.warning(f"No student record found for user: {user_id}")
                    profile_data["additional_info"] = {"roll_no": "N/A", "semester": "N/A"}
            except Exception as e:
                logger.error(f"Error fetching student profile: {str(e)}")
                profile_data["additional_info"] = {"roll_no": "N/A", "semester": "N/A"}
                
        elif user_role == 'teacher':
            try:
                teacher_response = supabase_admin.table('teachers')\
                    .select('*')\
                    .eq('id', user_id)\
                    .execute()
                if teacher_response.data:
                    teacher = teacher_response.data[0]
                    profile_data["profile_pic"] = teacher.get('profile_pic')
                    
                    if not profile_data["phone"]:
                        profile_data["phone"] = teacher.get('phone_number')
                    if not profile_data["address"]:
                        profile_data["address"] = teacher.get('address')
                    
                    profile_data["additional_info"] = {
                        "employee_id": teacher.get('teacher_id', 'N/A')
                    }
                    logger.info(f"Teacher profile data fetched for user: {user_id}")
                else:
                    logger.warning(f"No teacher record found for user: {user_id}")
                    profile_data["additional_info"] = {"employee_id": "N/A"}
            except Exception as e:
                logger.error(f"Error fetching teacher profile: {str(e)}")
                profile_data["additional_info"] = {"employee_id": "N/A"}
        
        return profile_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Profile error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@app.put("/api/user/{user_id}/profile")
def update_user_profile(user_id: str, request: dict):
    """Update user profile (phone and address only) - updates both users and role-specific tables"""
    try:
        logger.info(f"Updating profile for user: {user_id}")
        
        # Get user data to determine role
        user_response = supabase_admin.table('users').select('role').eq('id', user_id).execute()
        
        if not user_response.data:
            logger.warning(f"User not found: {user_id}")
            raise HTTPException(status_code=404, detail="User not found")
        
        user_role = user_response.data[0].get('role', '').lower()
        
        # Prepare update data
        update_data = {}
        if 'phone' in request:
            update_data['phone_number'] = request['phone']
        if 'address' in request:
            update_data['address'] = request['address']
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        # Update the users table first
        users_update_data = {}
        if 'phone' in request:
            users_update_data['phone_number'] = request['phone']
        if 'address' in request:
            users_update_data['address'] = request['address']
        
        if users_update_data:
            users_response = supabase_admin.table('users')\
                .update(users_update_data)\
                .eq('id', user_id)\
                .execute()
            
            if not users_response.data:
                logger.warning(f"Failed to update users table for user: {user_id}")
            else:
                logger.info(f"Users table updated successfully for user: {user_id}")
        
        # Update the role-specific table
        if user_role == 'student':
            response = supabase_admin.table('students')\
                .update(update_data)\
                .eq('id', user_id)\
                .execute()
            
            if not response.data:
                check_response = supabase_admin.table('students')\
                    .select('id')\
                    .eq('id', user_id)\
                    .execute()
                
                if not check_response.data:
                    logger.info(f"Creating student record for user: {user_id}")
                    student_data = {
                        'id': user_id,
                        'full_name': user_response.data[0].get('full_name', ''),
                        'email': user_response.data[0].get('email', ''),
                    }
                    if 'phone' in request:
                        student_data['phone_number'] = request['phone']
                    if 'address' in request:
                        student_data['address'] = request['address']
                    
                    insert_response = supabase_admin.table('students')\
                        .insert(student_data)\
                        .execute()
                    
                    if not insert_response.data:
                        raise HTTPException(status_code=500, detail="Failed to create student record")
                else:
                    raise HTTPException(status_code=500, detail="Failed to update student record")
                    
        elif user_role == 'teacher':
            response = supabase_admin.table('teachers')\
                .update(update_data)\
                .eq('id', user_id)\
                .execute()
            
            if not response.data:
                check_response = supabase_admin.table('teachers')\
                    .select('id')\
                    .eq('id', user_id)\
                    .execute()
                
                if not check_response.data:
                    logger.info(f"Creating teacher record for user: {user_id}")
                    teacher_data = {
                        'id': user_id,
                        'full_name': user_response.data[0].get('full_name', ''),
                        'email': user_response.data[0].get('email', ''),
                        'teacher_id': f"T{user_id[:8]}",
                    }
                    if 'phone' in request:
                        teacher_data['phone_number'] = request['phone']
                    if 'address' in request:
                        teacher_data['address'] = request['address']
                    
                    insert_response = supabase_admin.table('teachers')\
                        .insert(teacher_data)\
                        .execute()
                    
                    if not insert_response.data:
                        raise HTTPException(status_code=500, detail="Failed to create teacher record")
                else:
                    raise HTTPException(status_code=500, detail="Failed to update teacher record")
        else:
            raise HTTPException(status_code=400, detail="Invalid user role")
        
        logger.info(f"Profile updated successfully for user: {user_id}")
        
        return {
            "success": True,
            "phone": request.get('phone'),
            "address": request.get('address'),
            "message": "Profile updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Profile update error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@app.post("/api/user/{user_id}/profile-picture")
async def update_profile_picture(user_id: str, image: UploadFile = File(...)):
    """Update user profile picture"""
    try:
        logger.info(f"Updating profile picture for user: {user_id}")
        
        if not image.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        file_size = 0
        content = await image.read()
        file_size = len(content)
        if file_size > 5 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="Image size should be less than 5MB")
        
        import base64
        base64_image = base64.b64encode(content).decode('utf-8')
        image_data_url = f"data:{image.content_type};base64,{base64_image}"
        
        user_response = supabase_admin.table('users').select('role').eq('id', user_id).execute()
        
        if not user_response.data:
            logger.warning(f"User not found: {user_id}")
            raise HTTPException(status_code=404, detail="User not found")
        
        user_role = user_response.data[0].get('role', '').lower()
        
        users_response = supabase_admin.table('users')\
            .update({'profile_pic': image_data_url})\
            .eq('id', user_id)\
            .execute()
        
        if not users_response.data:
            raise HTTPException(status_code=500, detail="Failed to update user profile picture")
        
        if user_role == 'student':
            response = supabase_admin.table('students')\
                .update({'profile_pic': image_data_url})\
                .eq('id', user_id)\
                .execute()
        elif user_role == 'teacher':
            response = supabase_admin.table('teachers')\
                .update({'profile_pic': image_data_url})\
                .eq('id', user_id)\
                .execute()
        else:
            logger.info(f"Profile picture updated for user role: {user_role}")
        
        logger.info(f"Profile picture updated successfully for user: {user_id}")
        
        return {
            "success": True,
            "profile_pic": image_data_url,
            "message": "Profile picture updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Profile picture update error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")
            
@app.get("/api/student/{student_id}/dashboard")
def get_student_dashboard(student_id: str):
    """Get student dashboard data"""
    try:
        student_response = supabase_admin.table('students')\
            .select('*, users(full_name)')\
            .eq('id', student_id)\
            .execute()
        
        if not student_response.data:
            raise HTTPException(status_code=404, detail="Student not found")
        
        student = student_response.data[0]
        
        results_response = supabase_admin.table('results')\
            .select('*, subjects(name)')\
            .eq('student_id', student_id)\
            .execute()
        results = results_response.data
        
        total_percentage = sum(r['percentage'] for r in results) / len(results) if results else 0
        
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

@app.get("/api/students")
def get_students_by_faculty_semester(faculty: str, semester: str):
    """Get students by faculty and semester"""
    try:
        logger.info(f"Fetching students for faculty: {faculty}, semester: {semester}")
        
        # Extract semester number from string (e.g., "5th Semester" -> 5)
        import re
        semester_number = re.search(r'(\d+)', semester)
        if semester_number:
            semester_int = int(semester_number.group(1))
        else:
            semester_int = 1  # Default to 1 if no number found
        
        # Query students table with filters
        response = supabase_admin.table('students')\
            .select('*')\
            .eq('faculty', faculty)\
            .eq('semester', semester_int)\
            .execute()
        
        if not response.data:
            logger.info(f"No students found for faculty: {faculty}, semester: {semester}")
            return []
        
        # Sort by roll number - FIXED: handle both string and integer roll numbers
        students = sorted(response.data, key=lambda x: int(x.get('roll_no', 0)) if x.get('roll_no') is not None else 0)
        
        # Format response - convert semester back to string format
        student_list = []
        for student in students:
            sem = student.get('semester')
            # Convert semester back to string format
            if sem is not None:
                if sem == 1:
                    sem_str = "1st Semester"
                elif sem == 2:
                    sem_str = "2nd Semester"
                elif sem == 3:
                    sem_str = "3rd Semester"
                else:
                    sem_str = f"{sem}th Semester"
            else:
                sem_str = "N/A"
                
            student_list.append({
                "id": student.get('id'),
                "full_name": student.get('full_name'),
                "roll_no": str(student.get('roll_no', 'N/A')),  # Convert to string
                "faculty": student.get('faculty'),
                "semester": sem_str,
                "email": student.get('email'),
                "phone_number": student.get('phone_number'),
                "profile_pic": student.get('profile_pic')
            })
        
        logger.info(f"Found {len(student_list)} students")
        return student_list
        
    except Exception as e:
        logger.error(f"Get students error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@app.post("/api/attendance")
def submit_attendance(request: AttendanceSubmit):
    """Submit attendance for multiple students"""
    try:
        logger.info(f"Submitting attendance for teacher: {request.teacher_id}")
        
        if not request.attendance:
            raise HTTPException(status_code=400, detail="No attendance data provided")
        
        # Prepare attendance records for insertion
        attendance_records = []
        for record in request.attendance:
            # Check if attendance already exists for this student, subject, and date
            existing = supabase_admin.table('attendance')\
                .select('id')\
                .eq('student_id', record.student_id)\
                .eq('subject', record.subject)\
                .eq('date', record.date)\
                .execute()
            
            if existing.data:
                # Update existing record
                update_response = supabase_admin.table('attendance')\
                    .update({
                        'status': record.status,
                        'faculty': record.faculty,
                        'semester': record.semester,
                        'teacher_id': record.teacher_id,
                        'updated_at': datetime.now().isoformat()
                    })\
                    .eq('id', existing.data[0]['id'])\
                    .execute()
                
                if not update_response.data:
                    logger.warning(f"Failed to update attendance for student: {record.student_id}")
                else:
                    logger.info(f"Updated attendance for student: {record.student_id}")
            else:
                # Insert new record
                attendance_record = {
                    "student_id": record.student_id,
                    "subject": record.subject,
                    "faculty": record.faculty,
                    "semester": record.semester,
                    "date": record.date,
                    "status": record.status,
                    "teacher_id": record.teacher_id,
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat()
                }
                attendance_records.append(attendance_record)
        
        # Insert new records if any
        if attendance_records:
            insert_response = supabase_admin.table('attendance')\
                .insert(attendance_records)\
                .execute()
            
            if not insert_response.data:
                raise HTTPException(status_code=500, detail="Failed to submit attendance")
            
            logger.info(f"Inserted {len(attendance_records)} new attendance records")
        
        logger.info(f"Attendance submitted successfully for teacher: {request.teacher_id}")
        
        return {
            "success": True,
            "message": f"Attendance submitted successfully",
            "total": len(request.attendance),
            "updated": len(request.attendance) - len(attendance_records),
            "inserted": len(attendance_records)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Submit attendance error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@app.get("/api/attendance/teacher/{teacher_id}")
def get_teacher_attendance(teacher_id: str, date: Optional[str] = None):
    """Get attendance records for a teacher"""
    try:
        logger.info(f"Fetching attendance for teacher: {teacher_id}")
        
        query = supabase_admin.table('attendance')\
            .select('*')\
            .eq('teacher_id', teacher_id)
        
        if date:
            query = query.eq('date', date)
        
        response = query.order('date', desc=True).execute()
        
        if not response.data:
            return []
        
        return response.data
        
    except Exception as e:
        logger.error(f"Get teacher attendance error: {str(e)}")
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
        teacher_response = supabase_admin.table('teachers')\
            .select('*, users(full_name)')\
            .eq('id', teacher_id)\
            .execute()
        
        if not teacher_response.data:
            raise HTTPException(status_code=404, detail="Teacher not found")
        
        teacher = teacher_response.data[0]
        
        subjects_response = supabase_admin.table('subjects')\
            .select('*')\
            .eq('teacher_id', teacher_id)\
            .execute()
        subjects = subjects_response.data
        subject_ids = [s['id'] for s in subjects]
        
        students_count = 0
        if subject_ids:
            for subject_id in subject_ids:
                subject = next((s for s in subjects if s['id'] == subject_id), None)
                if subject and subject.get('class_id'):
                    count_response = supabase_admin.table('students')\
                        .select('*', count='exact')\
                        .eq('class_id', subject['class_id'])\
                        .execute()
                    students_count += len(count_response.data)
        
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

@app.post("/api/notes")
def create_note(request: NoteCreate, user_id: str = None):
    """Create a new note"""
    try:
        logger.info(f"Creating note for teacher: {user_id}")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        teacher_response = supabase_admin.table('users')\
            .select('id, full_name')\
            .eq('id', user_id)\
            .execute()
        
        if not teacher_response.data:
            raise HTTPException(status_code=404, detail="Teacher not found")
        
        teacher = teacher_response.data[0]
        
        note_data = {
            "teacher_id": user_id,
            "teacher_name": teacher['full_name'],
            "faculty": request.faculty,
            "semester": request.semester,
            "subject": request.subject,
            "topic": request.topic,
            "description": request.description,
            "attachments": json.dumps(request.attachments),
            "created_at": datetime.now().isoformat()
        }
        
        response = supabase_admin.table('notes')\
            .insert(note_data)\
            .execute()
        
        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to create note")
        
        note = response.data[0]
        
        note_response = {
            "id": note['id'],
            "teacher_id": note['teacher_id'],
            "teacher_name": note['teacher_name'],
            "faculty": note['faculty'],
            "semester": note['semester'],
            "subject": note['subject'],
            "topic": note['topic'],
            "description": note.get('description'),
            "attachments": json.loads(note['attachments']) if note.get('attachments') else [],
            "created_at": note['created_at']
        }
        
        logger.info(f"Note created successfully with ID: {note['id']}")
        return note_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create note error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@app.get("/api/notes/teacher/{teacher_id}")
def get_teacher_notes(teacher_id: str, limit: Optional[int] = None):
    """Get notes for a specific teacher"""
    try:
        logger.info(f"Fetching notes for teacher: {teacher_id}")
        
        query = supabase_admin.table('notes')\
            .select('*')\
            .eq('teacher_id', teacher_id)\
            .order('created_at', desc=True)
        
        if limit:
            query = query.limit(limit)
        
        response = query.execute()
        
        if not response.data:
            return []
        
        notes = []
        for note in response.data:
            notes.append({
                "id": note['id'],
                "teacher_id": note['teacher_id'],
                "teacher_name": note['teacher_name'],
                "faculty": note['faculty'],
                "semester": note['semester'],
                "subject": note['subject'],
                "topic": note['topic'],
                "description": note.get('description'),
                "attachments": json.loads(note['attachments']) if note.get('attachments') else [],
                "created_at": note['created_at']
            })
        
        logger.info(f"Found {len(notes)} notes for teacher: {teacher_id}")
        return notes
        
    except Exception as e:
        logger.error(f"Get teacher notes error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@app.delete("/api/notes/{note_id}")
def delete_note(note_id: str, user_id: str = None):
    """Delete a note"""
    try:
        logger.info(f"Deleting note: {note_id} for user: {user_id}")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        note_response = supabase_admin.table('notes')\
            .select('teacher_id')\
            .eq('id', note_id)\
            .execute()
        
        if not note_response.data:
            raise HTTPException(status_code=404, detail="Note not found")
        
        if note_response.data[0]['teacher_id'] != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to delete this note")
        
        response = supabase_admin.table('notes')\
            .delete()\
            .eq('id', note_id)\
            .execute()
        
        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to delete note")
        
        logger.info(f"Note deleted successfully: {note_id}")
        return {"success": True, "message": "Note deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete note error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@app.get("/api/health")
def health_check():
    """Health check endpoint"""
    try:
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