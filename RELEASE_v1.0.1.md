# SuperDiagnosticTool v1.0.1 - Critical Hotfix

## Critical Bug Fix

### API Key Persistence Issue (RESOLVED)

**Problem:**  
API key was not persisting between program runs, forcing users to re-enter it every session.

**Root Causes Discovered:**

1. **Over-aggressive Sanitization**
   - `re.sub(r'[^a-zA-Z0-9\-\._]', '', key)` was stripping valid characters from API keys
   - Solution: Replaced with simple `.strip()` to only remove whitespace

2. **Working Directory Confusion**
   - Script used `os.getcwd()` to determine save location
   - Keys were saved to different directories depending on where program was run
   - Solution: Use `SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))`

3. **Environment Variable Conflict**
   - Old/invalid API key stored in Windows Environment Variable `GEMINI_API_KEY`
   - Environment variable took precedence over file
   - Solution: Added validation for env var, clear instructions to remove old keys

---

## Download

**Standalone Windows Executable:**
- [SuperDiagnosticTool.exe](https://github.com/Guettaf-hossam/SuperDiagnosticTool/releases/download/v1.0.1/SuperDiagnosticTool.exe)

---

## Upgrade from v1.0

If upgrading from v1.0:

1. **Clear old environment variable** (if present):
   ```powershell
   Remove-Item env:GEMINI_API_KEY
   [System.Environment]::SetEnvironmentVariable('GEMINI_API_KEY', $null, 'User')
   ```

2. **Delete old key file** (optional cleanup):
   ```powershell
   Remove-Item gemini.key -ErrorAction SilentlyContinue
   ```

3. **Download v1.0.1**

4. **Run and enter API key once** - it will now persist correctly!

---

## What's Fixed

### API Key Handling
- Keys now persist between sessions
- Saved to script directory regardless of run location
- UTF-8 encoding prevents corruption
- Visible input supports Ctrl+V paste
- Validation loop prevents empty keys
- Corrupted key files auto-deleted

### Error Handling
- Clear error messages instead of silent failures
- Proper exception handling with diagnostics
- User-friendly feedback during input

---

## Full Changelog

See [CHANGELOG.md](CHANGELOG.md) for complete technical details.

---

## Thanks

Special thanks to the community for reporting this issue and helping debug!

**Full Comparison**: [v1.0.0...v1.0.1](https://github.com/Guettaf-hossam/SuperDiagnosticTool/compare/v1.0.0...v1.0.1)
