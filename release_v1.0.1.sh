# Git Commands for v1.0.1 Release

# Step 1: Stage all changes
git add .

# Step 2: Commit with descriptive message
git commit -m "v1.0.1 - Critical Hotfix: API Key Persistence

- Fixed API key not saving correctly between sessions
- Removed over-aggressive regex sanitization
- Added UTF-8 encoding for file operations
- Improved error messages and diagnostics"

# Step 3: Create annotated tag
git tag -a v1.0.1 -m "v1.0.1 - Critical Hotfix

Fixes:
- API key persistence bug
- Character corruption in saved keys
- Silent error handling

Changes:
- Visible API key input (supports Ctrl+V)
- UTF-8 encoding for all file I/O
- Better error messages"

# Step 4: Push to GitHub
git push origin main
git push origin v1.0.1

# Step 5: Build the executable (if needed)
# python build.py

echo "✅ Ready to create GitHub release at:"
echo "https://github.com/Guettaf-hossam/SuperDiagnosticTool/releases/new?tag=v1.0.1"
