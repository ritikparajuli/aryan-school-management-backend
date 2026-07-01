# Aryan School Management System - Backend

## API Server

This is the backend API server for the Aryan School Management System built with FastAPI and Supabase.

## Features

- 🔐 **Authentication** - Login/Register functionality
- 📊 **Attendance Management** - Mark and track attendance
- 📝 **Assignment Management** - Upload and manage assignments
- 🎯 **Results Management** - Add and view results
- 👨‍🎓 **Student Management** - Manage student records
- 👨‍🏫 **Teacher Management** - Manage teacher records
- 💬 **Messaging System** - Communication between users
- 🔒 **Security** - JWT authentication and role-based access

## Technologies Used

- **Python 3.14+** - Programming Language
- **FastAPI** - Modern web framework
- **Supabase** - Backend-as-a-Service (PostgreSQL)
- **Pydantic** - Data validation
- **Python-dotenv** - Environment variables management

## Installation

### Prerequisites
- Python 3.14 or higher
- pip (Python package manager)
- Supabase account

### Setup

```bash
# Clone the repository
git clone https://github.com/ritikparajuli/aryan-school-management-backend.git
cd aryan-school-management-backend

# Install dependencies
pip install -r requirements.txt

# Create .env file and add your credentials
# Start the server
python main.py
```

## Development

```bash
# Run in development mode with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Or run directly
python main.py
```

### Project Structure

```
├── .env
├── database.py
├── generate-readme.cjs
├── main.py
├── models.py
├── README.md
├── requirements.txt
└── supabase_client.py
```

### Environment Variables

Create a `.env` file in the root directory:

```env
# Supabase Configuration
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_supabase_service_role_key
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/login` | User login with role-based redirect |
| GET | `/api/health` | Health check endpoint |
| GET | `/api/student/{id}/dashboard` | Get student dashboard data |
| GET | `/api/student/{id}/results` | Get student results |
| GET | `/api/student/{id}/attendance` | Get student attendance |
| GET | `/api/teacher/{id}/dashboard` | Get teacher dashboard data |
| GET | `/api/teacher/{id}/assignments` | Get teacher assignments |
| GET | `/api/assignments` | Get all assignments |

## Database Schema

### Users Table
- `id` (integer, primary key)
- `email` (string, unique)
- `password` (string) - Store hashed passwords in production
- `role` (string) - 'student' or 'teacher'
- `full_name` (string)

### Students Table
- `id` (integer, primary key)
- `user_id` (integer, foreign key to users)
- `roll_number` (string, unique)
- `class_id` (integer, foreign key to classes)
- `date_of_birth` (date)
- `phone` (string)
- `parent_phone` (string)
- `address` (text)
- `profile_pic` (text)

### Teachers Table
- `id` (integer, primary key)
- `user_id` (integer, foreign key to users)
- `employee_id` (string, unique)
- `department` (string)
- `phone` (string)
- `profile_pic` (text)

### Classes Table
- `id` (integer, primary key)
- `name` (string)
- `section` (string)
- `academic_year` (string)

### Subjects Table
- `id` (integer, primary key)
- `name` (string)
- `code` (string, unique)
- `class_id` (integer, foreign key to classes)
- `teacher_id` (integer, foreign key to teachers)
- `credits` (integer)

### Attendance Table
- `id` (integer, primary key)
- `student_id` (integer, foreign key to students)
- `subject_id` (integer, foreign key to subjects)
- `date` (date)
- `status` (string) - 'present' or 'absent'
- `marked_by` (integer, foreign key to teachers)

### Assignments Table
- `id` (integer, primary key)
- `subject_id` (integer, foreign key to subjects)
- `title` (string)
- `description` (text)
- `file_url` (text)
- `total_marks` (integer)
- `due_date` (date)
- `uploaded_by` (integer, foreign key to teachers)

### Results Table
- `id` (integer, primary key)
- `student_id` (integer, foreign key to students)
- `subject_id` (integer, foreign key to subjects)
- `exam_type` (string)
- `marks_obtained` (float)
- `total_marks` (float)
- `grade` (string)
- `percentage` (float)

## Security Notes

⚠️ **Important Security Considerations:**
1. **Password Hashing**: In production, implement proper password hashing using `bcrypt` or `argon2`
2. **JWT Tokens**: Use JWT for session management instead of storing user data in localStorage
3. **Environment Variables**: Never commit `.env` file to version control
4. **CORS**: Restrict CORS origins in production to your frontend domain only
5. **Rate Limiting**: Implement rate limiting for login attempts

## Troubleshooting

### Common Issues

**1. Permission denied for table users**
```sql
-- Run in Supabase SQL Editor
GRANT SELECT ON users TO anon;
GRANT ALL ON ALL TABLES IN SCHEMA public TO anon;
```

**2. Column 'password_hash' not found**
- Check your users table schema. The column might be named 'password' instead.

**3. Connection timeout**
- Check your SUPABASE_URL in .env
- Ensure your IP is allowed in Supabase network restrictions

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT © Aryan College

## Contact

- **Author**: Ritik Parajuli
- **GitHub**: [@ritikparajuli](https://github.com/ritikparajuli)

## Acknowledgments

- Built with ❤️ for Aryan College
- Special thanks to all contributors
