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

    const filtered = sorted.filter(item => {
        const exclude = ['__pycache__', '.git', 'venv', 'env', 'node_modules', '.vscode', '.idea'];
        const fullPath = path.join(dir, item);
        try {
            const isDir = fs.statSync(fullPath).isDirectory();
            if (isDir) return !exclude.includes(item) && !item.startsWith('.');
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

// Write just the folder structure to README
const readmeContent = '```\n' + rootStructure + '```\n';

fs.writeFileSync('README.md', readmeContent);
console.log('✅ README.md created with folder structure only!');