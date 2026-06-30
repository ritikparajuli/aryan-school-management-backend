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
# Run in development mode
uvicorn main:app --reload

# Run tests
python test_db.py
python test_supabase.py
python test_final.py
```

### Project Structure

```
├── database.py
├── generate-readme.cjs
├── main.py
├── models.py
├── README.md
├── supabase_client.py
├── test_db.py
├── test_dns.py
├── test_final.py
├── test_supabase_api.py
└── test_supabase.py
```

### Environment Variables

Create a `.env` file in the root directory:

```env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/login` | User login |
| GET | `/api/students` | Get all students |
| POST | `/api/students` | Add new student |
| GET | `/api/teachers` | Get all teachers |
| POST | `/api/attendance` | Mark attendance |
| GET | `/api/results` | Get results |
| POST | `/api/results` | Add results |
| GET | `/api/messages` | Get messages |
| POST | `/api/messages` | Send message |

## Database Schema

- **Users** (id, name, email, password_hash, role)
- **Students** (id, user_id, class, section, roll_no)
- **Teachers** (id, user_id, department, qualification)
- **Attendance** (id, student_id, date, status, subject)
- **Assignments** (id, title, description, deadline, teacher_id)
- **Results** (id, student_id, subject, marks, grade)
- **Messages** (id, sender_id, receiver_id, content, timestamp)

## Testing

```bash
# Run database tests
python test_db.py

# Run Supabase tests
python test_supabase.py

# Run final integration tests
python test_final.py
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT © Aryan College

## Live Demo

[Coming Soon]

## Contact

- **Author**: Ritik Parajuli
- **GitHub**: [@ritikparajuli](https://github.com/ritikparajuli)

## Acknowledgments

- Built with ❤️ for Aryan College
- Special thanks to all contributors
