# SuperDiagnosticTool v1.0.1 - Critical Hotfix 🔧

## 🐛 Bug Fixes

### API Key Persistence Issue (Critical)
Fixed a critical bug where the API key was not being saved correctly, forcing users to re-enter it on every launch.

**Root Cause:**
- Over-aggressive regex sanitization (`re.sub()`) was corrupting the API key during save
- Missing UTF-8 encoding caused character corruption
- Silent error handling prevented users from seeing what went wrong

**What Changed:**
- ✅ Removed destructive regex that was stripping valid API key characters
- ✅ Added UTF-8 encoding for proper file handling
- ✅ Improved error messages with diagnostic information
- ✅ Added confirmation message when loading saved key

**User Impact:**
- **Before:** Had to re-enter API key every time the program started
- **After:** API key is saved correctly and loaded automatically on subsequent runs

---

## 📥 Download

**Windows Executable (Standalone):**
- `SuperDiagnosticTool.exe` - No Python installation required

---

## 🔄 Upgrade Instructions

If you're upgrading from v1.0:
1. Delete your old `gemini.key` file (if it exists)
2. Download the new v1.0.1 executable
3. Run the program and enter your API key once
4. The key will now persist correctly between sessions

---

## 📋 Full Changelog

### Changed
- Improved API key input UX with visible input (supports Ctrl+V paste)
- Enhanced file I/O with explicit UTF-8 encoding
- Better error handling with user-friendly messages

### Fixed
- **Critical:** API key not persisting between sessions
- **Critical:** Key corruption due to over-sanitization

### Technical Details
- Removed `re.sub(r'[^a-zA-Z0-9\-\._]', '', key)` sanitization
- Added `encoding="utf-8"` to all file operations
- Replaced silent `except: pass` with informative error messages

---

## 🙏 Credits

Thanks to the community for reporting this issue!

**Full Changelog**: https://github.com/Guettaf-hossam/SuperDiagnosticTool/compare/v1.0...v1.0.1
