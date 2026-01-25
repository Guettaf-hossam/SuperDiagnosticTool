# PowerShell Script for v1.0.1 Release
# Run this in Git Bash or PowerShell with Git installed

Write-Host "🚀 Starting v1.0.1 Release Process..." -ForegroundColor Cyan

# Step 1: Stage all changes
Write-Host "`n📦 Staging changes..." -ForegroundColor Yellow
git add .

# Step 2: Commit
Write-Host "`n💾 Committing changes..." -ForegroundColor Yellow
git commit -m "v1.0.1 - Critical Hotfix: API Key Persistence

- Fixed API key not saving correctly between sessions
- Removed over-aggressive regex sanitization
- Added UTF-8 encoding for file operations
- Improved error messages and diagnostics"

# Step 3: Create tag
Write-Host "`n🏷️  Creating tag v1.0.1..." -ForegroundColor Yellow
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
Write-Host "`n⬆️  Pushing to GitHub..." -ForegroundColor Yellow
git push origin main
git push origin v1.0.1

# Step 5: Build executable (optional)
Write-Host "`n🔨 Do you want to build the executable now? (Y/N)" -ForegroundColor Cyan
$build = Read-Host
if ($build -eq "Y" -or $build -eq "y") {
    Write-Host "Building executable..." -ForegroundColor Yellow
    python build.py
    Write-Host "✅ Build complete! Check dist/ folder" -ForegroundColor Green
}

Write-Host "`n✅ Release v1.0.1 is ready!" -ForegroundColor Green
Write-Host "`n📝 Next steps:" -ForegroundColor Cyan
Write-Host "1. Go to: https://github.com/Guettaf-hossam/SuperDiagnosticTool/releases/new?tag=v1.0.1"
Write-Host "2. Copy content from RELEASE_v1.0.1.md"
Write-Host "3. Upload dist/SuperDiagnosticTool.exe"
Write-Host "4. Click 'Publish release'"
