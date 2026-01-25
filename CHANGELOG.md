# Changelog

All notable changes to SuperDiagnosticTool will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.1] - 2026-01-25

### Fixed
- **CRITICAL:** API key not persisting between program sessions
  - **Root Cause 1:** Over-aggressive regex sanitization (`re.sub`) was corrupting API keys during save
  - **Root Cause 2:** Script used `os.getcwd()` instead of script directory, causing keys to be saved in different locations
  - **Root Cause 3:** Old/invalid API key stored in Windows Environment Variable took precedence over file
  - Removed destructive regex sanitization - now uses simple `.strip()` only
  - Changed to use `SCRIPT_DIR` instead of current working directory
  - Added UTF-8 encoding to all file operations
  - Improved error messages and added detailed logging

### Changed
- API key input now shows characters (visible input) to support Ctrl+V paste on Windows
- Added validation loop - program won't proceed with empty/invalid key
- Enhanced file I/O operations with explicit UTF-8 encoding
- Added automatic deletion of corrupted key files
- Improved error handling with user-friendly messages
- Added validation before `genai.configure()` to prevent silent failures

### Security
- Added internal integrity verification system
- Implemented memory-safe execution patterns
- Enhanced code signing readiness
- Added core logic validation signatures
- Debug logging to track API key loading process
- Better user feedback during key input process

### Added
- New validation function `validate_key()` to check API key format
- Error handling for environment variable conflicts

### Technical
- Replaced `re.sub(r'[^a-zA-Z0-9\-\._]', '', key)` with `.strip()`
- Added `SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))`
- Added `encoding="utf-8"` parameter to all `open()` calls
- Replaced `except: pass` with proper exception handling
- Changed `return ""` to `sys.exit(1)` for invalid input
- Added environment variable validation before using `os.getenv()`


---

## [1.0.0] - 2026-01-24

### Added
- Initial production release
- AI-powered system diagnostics using Google Gemini 2.5 Flash
- Universal hardware support (1-128+ CPU cores)
- Automated PowerShell remediation scripts
- Professional HTML reports with dark theme
- Security-first architecture with 6-layer validation
- Automatic system restore point creation
- Custom diagnostic icon with "Pulse" design
- Comprehensive system scanning:
  - CPU, RAM, Disk health
  - Network diagnostics
  - Security integrity checks
  - Event log analysis
  - Bluetooth status
  - GPU information
  - Startup applications
  - Failed services detection

### Security
- Multi-level script validation before execution
- Dry-run simulation mode
- User confirmation required for all changes
- System restore point integration
- Monitored execution with change detection

---

## Release Types

- **Major (X.0.0):** Breaking changes, major new features
- **Minor (1.X.0):** New features, backward compatible
- **Patch (1.0.X):** Bug fixes, security patches

---

[1.0.1]: https://github.com/Guettaf-hossam/SuperDiagnosticTool/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/Guettaf-hossam/SuperDiagnosticTool/releases/tag/v1.0.0
