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

    const filtered = sorted.filter(item => {
        const exclude = ['__pycache__', '.git', 'venv', 'env', 'node_modules', '.vscode', '.idea'];
        const excludeFiles = ['.env', '.gitignore', '.DS_Store', 'requirements.txt'];
        const fullPath = path.join(dir, item);
        try {
            const isDir = fs.statSync(fullPath).isDirectory();
            if (isDir) return !exclude.includes(item) && !item.startsWith('.');
            else return !excludeFiles.includes(item) && !item.startsWith('.');
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
'# Run in development mode\n' +
'uvicorn main:app --reload\n\n' +
'# Run tests\n' +
'python test_db.py\n' +
'python test_supabase.py\n' +
'python test_final.py\n' +
'```\n\n' +
'### Project Structure\n\n' +
'```\n' +
rootStructure +
'```\n\n' +
'### Environment Variables\n\n' +
'Create a `.env` file in the root directory:\n\n' +
'```env\n' +
'SUPABASE_URL=your_supabase_url\n' +
'SUPABASE_KEY=your_supabase_key\n' +
'```\n\n' +
'## API Endpoints\n\n' +
'| Method | Endpoint | Description |\n' +
'|--------|----------|-------------|\n' +
'| POST | `/api/login` | User login |\n' +
'| GET | `/api/students` | Get all students |\n' +
'| POST | `/api/students` | Add new student |\n' +
'| GET | `/api/teachers` | Get all teachers |\n' +
'| POST | `/api/attendance` | Mark attendance |\n' +
'| GET | `/api/results` | Get results |\n' +
'| POST | `/api/results` | Add results |\n' +
'| GET | `/api/messages` | Get messages |\n' +
'| POST | `/api/messages` | Send message |\n\n' +
'## Database Schema\n\n' +
'- **Users** (id, name, email, password_hash, role)\n' +
'- **Students** (id, user_id, class, section, roll_no)\n' +
'- **Teachers** (id, user_id, department, qualification)\n' +
'- **Attendance** (id, student_id, date, status, subject)\n' +
'- **Assignments** (id, title, description, deadline, teacher_id)\n' +
'- **Results** (id, student_id, subject, marks, grade)\n' +
'- **Messages** (id, sender_id, receiver_id, content, timestamp)\n\n' +
'## Testing\n\n' +
'```bash\n' +
'# Run database tests\n' +
'python test_db.py\n\n' +
'# Run Supabase tests\n' +
'python test_supabase.py\n\n' +
'# Run final integration tests\n' +
'python test_final.py\n' +
'```\n\n' +
'## Contributing\n\n' +
'1. Fork the repository\n' +
'2. Create your feature branch (`git checkout -b feature/amazing-feature`)\n' +
'3. Commit your changes (`git commit -m \'Add some amazing feature\'`)\n' +
'4. Push to the branch (`git push origin feature/amazing-feature`)\n' +
'5. Open a Pull Request\n\n' +
'## License\n\n' +
'MIT © Aryan College\n\n' +
'## Live Demo\n\n' +
'[Coming Soon]\n\n' +
'## Contact\n\n' +
'- **Author**: Ritik Parajuli\n' +
'- **GitHub**: [@ritikparajuli](https://github.com/ritikparajuli)\n\n' +
'## Acknowledgments\n\n' +
'- Built with ❤️ for Aryan College\n' +
'- Special thanks to all contributors\n';

fs.writeFileSync('README.md', readmeContent);
console.log('✅ README.md created with complete project structure!');
console.log('📁 Structure includes all files and folders from your backend project!');