// generate-readme.cjs
const fs = require('fs');
const path = require('path');

function generateStructure(dir, prefix = '', depth = 0) {
    let structure = '';
    if (!fs.existsSync(dir) || depth > 3) return structure;
    
    const items = fs.readdirSync(dir);
    const sorted = items.sort((a, b) => {
        try {
            const aIsDir = fs.statSync(path.join(dir, a)).isDirectory();
            const bIsDir = fs.statSync(path.join(dir, b)).isDirectory();
            if (aIsDir && !bIsDir) return -1;
            if (!aIsDir && bIsDir) return 1;
            return a.localeCompare(b);
        } catch (e) { return 0; }
    });

    // Only exclude unnecessary system files
    const filtered = sorted.filter(item => {
        const exclude = ['__pycache__', '.git', 'venv', 'env', 'node_modules', '.vscode', '.idea'];
        const fullPath = path.join(dir, item);
        try {
            const isDir = fs.statSync(fullPath).isDirectory();
            if (isDir) return !exclude.includes(item) && !item.startsWith('.');
            // Show all files including .env, .gitignore, requirements.txt
            else return true;
        } catch (e) { return false; }
    });

    filtered.forEach((item, index) => {
        const fullPath = path.join(dir, item);
        const isLast = index === filtered.length - 1;
        const connector = isLast ? '└── ' : '├── ';
        const childPrefix = isLast ? '    ' : '│   ';
        try {
            const isDir = fs.statSync(fullPath).isDirectory();
            if (isDir) {
                structure += prefix + connector + item + '/\n';
                structure += generateStructure(fullPath, prefix + childPrefix, depth + 1);
            } else {
                structure += prefix + connector + item + '\n';
            }
        } catch (e) {}
    });
    return structure;
}

// Generate structure from root
const rootStructure = generateStructure('.', '', 0);

// Create README content
const readmeContent = '# Aryan School Management System - Backend\n\n' +
'## API Server\n\n' +
'This is the backend API server for the Aryan School Management System built with FastAPI and Supabase.\n\n' +
'## Features\n\n' +
'- 🔐 **Authentication** - Login/Register functionality\n' +
'- 📊 **Attendance Management** - Mark and track attendance\n' +
'- 📝 **Assignment Management** - Upload and manage assignments\n' +
'- 🎯 **Results Management** - Add and view results\n' +
'- 👨‍🎓 **Student Management** - Manage student records\n' +
'- 👨‍🏫 **Teacher Management** - Manage teacher records\n' +
'- 💬 **Messaging System** - Communication between users\n' +
'- 🔒 **Security** - JWT authentication and role-based access\n\n' +
'## Technologies Used\n\n' +
'- **Python 3.14+** - Programming Language\n' +
'- **FastAPI** - Modern web framework\n' +
'- **Supabase** - Backend-as-a-Service (PostgreSQL)\n' +
'- **Pydantic** - Data validation\n' +
'- **Python-dotenv** - Environment variables management\n\n' +
'## Installation\n\n' +
'### Prerequisites\n' +
'- Python 3.14 or higher\n' +
'- pip (Python package manager)\n' +
'- Supabase account\n\n' +
'### Setup\n\n' +
'```bash\n' +
'# Clone the repository\n' +
'git clone https://github.com/ritikparajuli/aryan-school-management-backend.git\n' +
'cd aryan-school-management-backend\n\n' +
'# Install dependencies\n' +
'pip install -r requirements.txt\n\n' +
'# Create .env file and add your credentials\n' +
'# Start the server\n' +
'python main.py\n' +
'```\n\n' +
'## Development\n\n' +
'```bash\n' +
'# Run in development mode with auto-reload\n' +
'uvicorn main:app --reload --host 0.0.0.0 --port 8000\n\n' +
'# Or run directly\n' +
'python main.py\n' +
'```\n\n' +
'### Project Structure\n\n' +
'```\n' +
rootStructure +
'```\n\n' +
'### Environment Variables\n\n' +
'Create a `.env` file in the root directory:\n\n' +
'```env\n' +
'# Supabase Configuration\n' +
'SUPABASE_URL=your_supabase_url\n' +
'SUPABASE_KEY=your_supabase_anon_key\n' +
'SUPABASE_SERVICE_KEY=your_supabase_service_role_key\n' +
'```\n\n' +
'## API Endpoints\n\n' +
'| Method | Endpoint | Description |\n' +
'|--------|----------|-------------|\n' +
'| POST | `/api/login` | User login with role-based redirect |\n' +
'| GET | `/api/health` | Health check endpoint |\n' +
'| GET | `/api/student/{id}/dashboard` | Get student dashboard data |\n' +
'| GET | `/api/student/{id}/results` | Get student results |\n' +
'| GET | `/api/student/{id}/attendance` | Get student attendance |\n' +
'| GET | `/api/teacher/{id}/dashboard` | Get teacher dashboard data |\n' +
'| GET | `/api/teacher/{id}/assignments` | Get teacher assignments |\n' +
'| GET | `/api/assignments` | Get all assignments |\n\n' +
'## Database Schema\n\n' +
'### Users Table\n' +
'- `id` (integer, primary key)\n' +
'- `email` (string, unique)\n' +
'- `password` (string) - Store hashed passwords in production\n' +
'- `role` (string) - \'student\' or \'teacher\'\n' +
'- `full_name` (string)\n\n' +
'### Students Table\n' +
'- `id` (integer, primary key)\n' +
'- `user_id` (integer, foreign key to users)\n' +
'- `roll_no` (string, unique)\n' +
'- `class_id` (integer, foreign key to classes)\n' +
'- `date_of_birth` (date)\n' +
'- `phone` (string)\n' +
'- `parent_phone` (string)\n' +
'- `address` (text)\n' +
'- `profile_pic` (text)\n\n' +
'### Teachers Table\n' +
'- `id` (integer, primary key)\n' +
'- `user_id` (integer, foreign key to users)\n' +
'- `employee_id` (string, unique)\n' +
'- `department` (string)\n' +
'- `phone` (string)\n' +
'- `profile_pic` (text)\n\n' +
'### Classes Table\n' +
'- `id` (integer, primary key)\n' +
'- `name` (string)\n' +
'- `section` (string)\n' +
'- `academic_year` (string)\n\n' +
'### Subjects Table\n' +
'- `id` (integer, primary key)\n' +
'- `name` (string)\n' +
'- `code` (string, unique)\n' +
'- `class_id` (integer, foreign key to classes)\n' +
'- `teacher_id` (integer, foreign key to teachers)\n' +
'- `credits` (integer)\n\n' +
'### Attendance Table\n' +
'- `id` (integer, primary key)\n' +
'- `student_id` (integer, foreign key to students)\n' +
'- `subject_id` (integer, foreign key to subjects)\n' +
'- `date` (date)\n' +
'- `status` (string) - \'present\' or \'absent\'\n' +
'- `marked_by` (integer, foreign key to teachers)\n\n' +
'### Assignments Table\n' +
'- `id` (integer, primary key)\n' +
'- `subject_id` (integer, foreign key to subjects)\n' +
'- `title` (string)\n' +
'- `description` (text)\n' +
'- `file_url` (text)\n' +
'- `total_marks` (integer)\n' +
'- `due_date` (date)\n' +
'- `uploaded_by` (integer, foreign key to teachers)\n\n' +
'### Results Table\n' +
'- `id` (integer, primary key)\n' +
'- `student_id` (integer, foreign key to students)\n' +
'- `subject_id` (integer, foreign key to subjects)\n' +
'- `exam_type` (string)\n' +
'- `marks_obtained` (float)\n' +
'- `total_marks` (float)\n' +
'- `grade` (string)\n' +
'- `percentage` (float)\n\n' +
'## Security Notes\n\n' +
'⚠️ **Important Security Considerations:**\n' +
'1. **Password Hashing**: In production, implement proper password hashing using `bcrypt` or `argon2`\n' +
'2. **JWT Tokens**: Use JWT for session management instead of storing user data in localStorage\n' +
'3. **Environment Variables**: Never commit `.env` file to version control\n' +
'4. **CORS**: Restrict CORS origins in production to your frontend domain only\n' +
'5. **Rate Limiting**: Implement rate limiting for login attempts\n\n' +
'## Troubleshooting\n\n' +
'### Common Issues\n\n' +
'**1. Permission denied for table users**\n' +
'```sql\n' +
'-- Run in Supabase SQL Editor\n' +
'GRANT SELECT ON users TO anon;\n' +
'GRANT ALL ON ALL TABLES IN SCHEMA public TO anon;\n' +
'```\n\n' +
'**2. Column \'password_hash\' not found**\n' +
'- Check your users table schema. The column might be named \'password\' instead.\n\n' +
'**3. Connection timeout**\n' +
'- Check your SUPABASE_URL in .env\n' +
'- Ensure your IP is allowed in Supabase network restrictions\n\n' +
'## Contributing\n\n' +
'1. Fork the repository\n' +
'2. Create your feature branch (`git checkout -b feature/amazing-feature`)\n' +
'3. Commit your changes (`git commit -m \'Add some amazing feature\'`)\n' +
'4. Push to the branch (`git push origin feature/amazing-feature`)\n' +
'5. Open a Pull Request\n\n' +
'## License\n\n' +
'MIT © Aryan College\n\n' +
'## Contact\n\n' +
'- **Author**: Ritik Parajuli\n' +
'- **GitHub**: [@ritikparajuli](https://github.com/ritikparajuli)\n\n' +
'## Acknowledgments\n\n' +
'- Built with ❤️ for Aryan College\n' +
'- Special thanks to all contributors\n';

fs.writeFileSync('README.md', readmeContent);
console.log('✅ README.md created with complete project structure!');
console.log('📁 Structure includes all files and folders from your backend project!');