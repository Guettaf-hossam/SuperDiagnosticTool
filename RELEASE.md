# SuperDiagnosticTool - Release Guide

## Building the EXE with Icon

### Step 1: Convert Icon (Automatic)
The build script will automatically convert the PNG icon to ICO format.

### Step 2: Build the EXE
```bash
python build_exe.py
```

This will create `dist/SuperDiagnosticTool.exe` with the embedded icon.

### Step 3: Test the EXE
```bash
cd dist
SuperDiagnosticTool.exe
```

## Creating a GitHub Release

### Step 1: Commit and Push
```bash
git add .
git commit -m "v1.0 - Official Release with Icon"
git push origin main
```

### Step 2: Create Tag
```bash
git tag -a v1.0 -m "v1.0 - Official Release"
git push origin v1.0
```

### Step 3: Upload to GitHub Release
1. Go to: https://github.com/Guettaf-hossam/SuperDiagnosticTool/releases/new
2. Select tag: v1.0
3. Release title: "v1.0 - Official Release"
4. Description:
```markdown
# SuperDiagnosticTool v1.0 - Official Release

First professional release with AI features

## What's New
- AI-powered system diagnostics using Google Gemini
- Universal hardware support (1-128+ CPU cores)
- Automated PowerShell remediation scripts
- Professional HTML reports
- Custom icon with "Diagnostic Pulse" design

## Download
- **Windows EXE:** SuperDiagnosticTool.exe (Standalone, no Python required)

## Requirements
- Windows 10/11
- Administrator privileges
- Google Gemini API Key

**Full Changelog**: https://github.com/Guettaf-hossam/SuperDiagnosticTool/commits/v1.0
```

5. Upload file: `dist/SuperDiagnosticTool.exe`
6. Click "Publish release"

## File Checklist
- [x] icon.ico (Windows icon format)
- [x] docs/icon.png (PNG for README)
- [x] dist/SuperDiagnosticTool.exe (Executable with icon)
- [x] README.md (Updated with icon)
- [x] LICENSE (GPL-3.0)
